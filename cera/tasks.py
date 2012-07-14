from celery import registry
from cera.models import DataArray, ModelRun, Variable
from cera.query import *
from cera import settings
from cera.views import WMSAdapter, WMS, metric

from ga_ows.tasks import DeferredRenderer
from celery.task import task
import os
from datetime import timedelta
from tempfile import NamedTemporaryFile
import netCDF4
import cPickle as pickle
from logging import getLogger

import numpy as np
from ga_ows.views import wms

_index = None
log = getLogger(__name__)

# copy netcdf file over OR open via OpenDAP and copy elements over into bare arrays
def get_remote_paths(when):
    for runid in settings.VALID_RUN_ID:
        run = settings.ADCIRC_MOUNTPOINT + settings.ADCIRC_NETCDF_PATH.format(
            yyyymmdd = when.strftime('%Y/%m/%d'),
            runid = runid)
        this_run = ModelRun.objects.filter(when=when+timedelta(hours=int(runid))).first()
        if not this_run and os.path.exists(run):
            ModelRun.objects.create(when=when+timedelta(hours=int(runid)), name=run, version=when.strftime('%Y%m%d') + runid)
            for filename in os.listdir(run):
                for var in settings.VARIABLES:
                    if ("max" + var) in filename:
                        yield runid, run, ("max" + var) , filename
                    elif var in filename:
                        yield runid, run, var, filename

# copy a path and gunzip it, because all netcdfs in NCFS are gzipped.
def copy_and_expand(orig, extn):
    log.info('copying and expanding {filename}'.format(filename=orig))
    tf = NamedTemporaryFile(suffix=extn)
    os.system('gzcat "{filename}" > {tempfile}'.format(filename=orig, tempfile=tf.name))
    return tf

# copy, expand, and provide tempfiles for all the netcdf files for a particular ADCIRC run.
def expand_all(when):
    log.info("copying and expanding all files for the newest run.")
    return [(runid, run, var, copy_and_expand(run + path, '.nc')) for runid, run, var, path in get_remote_paths(when)]

_triangles = None
def read_array(filename, varname, when):
    global _triangles

    log.info('reading {varname} array for {when}00 from {filename} '.format(
        varname=varname,
        filename=filename,
        when=when.strftime('%Y.%m.%d.%H')
    ))

    if not _triangles:
        _triangles = np.load(settings.BATHYMETRY_INDEX_FILE + '.nodes.npy')

    ds = netCDF4.Dataset(filename)
    for name, var in ds.variables.items():
        Variable.objects.get_or_create(basename=varname, name=name, long_name=var.long_name if hasattr(var, 'long_name') else name)
        dims = var.dimensions
        log.debug('reading {name} from {varname} with {dims}'.format(**locals()))
        if var.dimensions == settings.DATASET_DIMENSIONS:
            log.debug('loading {name} into database'.format(**locals()))
            for time in (int(t) for t in ds.variables['time']):
                arr = var[time,:]

                DataArray.objects.create(
                    basename = varname,
                    name = name,
                    long_name = var.long_name if hasattr(var, 'long_name') else name,
                    time = when + timedelta(hours=time),
                    data = pickle.dumps(arr, protocol = -1),
                    version = when.strftime('%Y%m%d%H')
                )


def read_arrays(when):
    log.info('reading arrays for run at {when}'.format(when=when.strftime('%Y.%m.%d.%H')))
    for runid, run, var, tempfile in expand_all(when):
        read_array(tempfile.name, var, when + timedelta(hours=int(runid)))



#
# Tasks below as opposed to functions
#
@task
class DeferredCERARenderer(DeferredRenderer):
    adapter = WMSAdapter(metric)
deferred_cera_renderer = registry.tasks[DeferredCERARenderer.name]

class DeferredWMSView(WMS):
    """Allows you to distribute the rendering across multiple machines for high volumes"""
    task = deferred_cera_renderer

@task
def deferred_values_for_triangles(*args, **kwargs):
    return list(values_for_triangles(*args, **kwargs))

@task
def deferred_mean_values_for_triangles(*args, **kwargs):
    return list(mean_values_for_triangles(*args, **kwargs))

@task
def deferred_bbox_values_for_triangles(*args, **kwargs):
    return list(bbox_values_for_triangles(*args, **kwargs))

@task
def deferred_bbox_mean_values_for_triangles(*args, **kwargs):
    return list(bbox_mean_values_for_triangles(*args, **kwargs))

@task
def deferred_value_nearest(*args, **kwargs):
    return value_nearest(*args, **kwargs)

@task(ignore_result=True)
def append_new_run():
    """
    Looks for the newest ADCIRC run on the NFS mount and if it's new, copies it over, appends file to the database
    Call graph::

        append_new_run -> read_arrays -> read_array(array)
            for all array in expand_all

        expand_all -> copy_and_expand(file)
            for all file in get_remote_paths

    """
    log.info('appending new ADCIRC run to the database')
    read_arrays(today())

# clean out old arrays
@task(ignore_result=True)
def remove_old_data():
    when = datetime.now()
    when = datetime(when.year, when.month, when.day) - settings.DELETE_ARRAYS_OLDER_THAN
    ModelRun.objects.filter(when__lt=when, hold=False).delete()
    DataArray.objects.filter(when__lt=when, hold=False).delete()

# clean out caches
@task(ignore_result=True)
def clean_web_cache():
    cache = wms.WMSCache('cera')
    cache.flush_lru(settings.MAXIMUM_CACHE_SIZE)

@task(ignore_result=True)
def destroy_bathymetry():
    global _index
    log.info("Destroying bathymetry")
    if os.path.exists(settings.BATHYMETRY_INDEX_FILE + 'bathymetry.spatialite'):
        os.unlink(settings.BATHYMETRY_INDEX_FILE + 'bathymetry.spatialite')
        os.unlink(settings.BATHYMETRY_INDEX_FILE + 'bathymetry.coords.npy')
        os.unlink(settings.BATHYMETRY_INDEX_FILE + 'bathymetry.nodes.npy')

    _index = None
