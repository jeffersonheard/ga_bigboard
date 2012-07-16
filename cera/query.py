__author__ = 'jeffersonheard'
# TODO - use triangle -> node# array to pre-compute mean for each triangle when adding DataArray objects.
# TODO - pre-compute Polygon objects instead of yielding them.  To say that it's monumentally inefficient to make Polygon objects every damn time is an understatement.

from datetime import datetime
from logging import getLogger
import os
import re
import cPickle as pickle
from django.contrib.gis.geos import Polygon
import numpy as np
from numpy.ma import masked
from threading import local

log = getLogger(__name__)

from ga_spatialnosql.index import GeoIndex
from cera import settings
from cera.models import *

_local = local()
_local.index = None
_index = None
_triangles = None
_triangle_coords = None

def today():
    when = datetime.now()
    when = datetime(when.year, when.month, when.day)
    return when


# index bathymetry.
def read_bathymetry_file():
    log.info('Building irregular-grid index from bathymetry file.  This will take awhile.')
    then = datetime.now()
    def take(k, source):
        while k>0:
            yield re.split(r'\s*', source.readline().strip())
            k -= 1

    src = open(settings.BATHYMETRY_SOURCE_FILE)
    version = src.readline().strip()
    num_edges, num_nodes = [int(k) for k in re.split(r'\s*', src.readline().strip())]

    log.info("Reading {num_edges} triangles from {num_nodes} total nodes".format(num_edges=num_edges, num_nodes=num_nodes))

    zvalues = np.empty(num_nodes+1, dtype=np.float_)
    nodes_arr = np.empty((num_nodes+1, 2), dtype=np.float_)
    triangle_arr = np.empty((num_edges+1, 3), dtype=np.int_)
    triangle_coords_arr = np.empty((num_edges+1, 3, 2), dtype=np.float_)
    #triangle_coords_arr = {}

    for node, x, y, z in take(num_nodes, src):
        node = int(node)
        nodes_arr[node][0] = float(x)
        nodes_arr[node][1] = float(y)
        zvalues[node] = z

    log.info('Built node array')

    for triangle, dim, node1, node2, node3 in take(num_edges, src):
        node1 = int(node1)
        node2 = int(node2)
        node3 = int(node3)
        triangle = int(triangle)

        triangle_arr[triangle][0] = node1
        triangle_arr[triangle][1] = node2
        triangle_arr[triangle][2] = node3

        triangle_coords_arr[triangle][0] = nodes_arr[node1]
        triangle_coords_arr[triangle][1] = nodes_arr[node2]
        triangle_coords_arr[triangle][2] = nodes_arr[node3]

        #triangle_coords_arr[triangle] = Polygon(( tuple(nodes_arr[node1]), tuple(nodes_arr[node2]), tuple(nodes_arr[node3]), tuple(nodes_arr[node1]) ), srid=4326)

    log.info('Built triangle array')

    obj = StaticArray.objects.filter(name='bathymetry', long_name='bathymetry').first() or StaticArray(name='bathymetry', long_name='bathymetry')
    obj.data = pickle.dumps(zvalues)
    obj.save()

    log.info('Saved bathymetry data')

    if os.path.exists(settings.BATHYMETRY_INDEX_FILE + '.idx'):
        os.unlink(settings.BATHYMETRY_INDEX_FILE + '.idx')
        os.unlink(settings.BATHYMETRY_INDEX_FILE + '.dat')

    index = GeoIndex(settings.BATHYMETRY_INDEX_FILE, 'bathymetry', str, int, clear=True) # bulk load

    cs = ((i, triangle_arr[i]) for i in range(1, triangle_arr.shape[0]))
    triangles = ((i, Polygon(( tuple(nodes_arr[c1]), tuple(nodes_arr[c2]), tuple(nodes_arr[c3]), tuple(nodes_arr[c1]) ), srid=4326) ) for i, (c1, c2, c3) in cs)
    index.bulk_insert(triangles)

    log.info('saved geometry index')

    np.save(settings.BATHYMETRY_INDEX_FILE + "bathymetry.nodes.npy", triangle_arr)
    log.info('saved nodes')
    np.save(settings.BATHYMETRY_INDEX_FILE + 'bathymetry.coords.npy', triangle_coords_arr)
    log.info('saved coordinates')

    index.close()
    delta = datetime.now() - then
    log.info('Finished building index in {secs} seconds.'.format(secs=delta.seconds))

def ensure_bathymetry_index():
    global _local, _triangles, _triangle_coords
    if not hasattr(_local, 'index') or not _local.index:
        if not os.path.exists(settings.BATHYMETRY_INDEX_FILE + 'bathymetry.spatialite'):
            read_bathymetry_file()
        _local.index = GeoIndex(settings.BATHYMETRY_INDEX_FILE, 'bathymetry', str, int)
        _triangles = np.load(settings.BATHYMETRY_INDEX_FILE + "bathymetry.nodes.npy")
        _triangle_coords = np.load(settings.BATHYMETRY_INDEX_FILE + 'bathymetry.coords.npy')
        log.info('loaded bathymetry index.')


def bbox_values_for_triangles(basename, varname, time, bbox, version=None):
    """
    Same as values_for_triangles, but give an interleaved bounding box instead (minx, miny, maxx, maxy). Faster than
    the other function, because no geometry comparison is done per triangle.
    """
    global _local, _var_cache
    ensure_bathymetry_index()
    x1,y1,x2,y2 = bbox
    bbox = Polygon(((x1,y1), (x2,y1), (x2,y2), (x1,y2), (x1,y1)), srid=4326)
    triangles = np.array(list(_local.index.bboverlaps(bbox)), dtype=np.int32)
    var = DataArray.objects.filter(basename=basename, name=varname, time__lte=time).order_by('-version')
    if version:
       var = var.filter(version=version)
    var = var.first()
    if var:
       var = pickle.loads(var.data)
    else:
       raise KeyError()

    node_matrix = np.take(_triangles, triangles, axis=0)
    geometry = np.take(_triangle_coords, triangles, axis=0)
    val_matrix = np.take(var, node_matrix-1)

    return geometry, val_matrix

def bbox_mean_values_for_triangles(basename, varname, time, bbox):
    """
    Same as mean_values_for_triangles, but give an interleaved bounding box instead (minx, miny, maxx, maxy). Faster than
    the other function, because no geometry comparison is done per triangle.
    """
    geometry, val_matrix = bbox_values_for_triangles(basename, varname, time, bbox)
    means = np.ma.mean(val_matrix, axis=1)

    geometry = np.ma.array(geometry)
    geomask = np.array(np.ma.getmask(means))
    geomask = np.dstack((geomask, geomask))
    geomask = np.dstack((geomask, geomask, geomask))
    geometry.mask = geomask

    means = means.compressed()
    geometry = geometry.compressed().reshape(means.shape[0], 3, 2)

    return geometry, means

def value_nearest(basename, varname, time, x, y, version=None):
    """
    Grab the nearest node value to the given lon/lat. This may be None if that's all that surrounds it.

    :param basename: The basis name for hte dataset, like "maxelev"
    :param varname: The variable short-name wthin the dataset, like "zeta"
    :param time: The time that we're seeking as a datetime object
    :param x: Longitude degrees
    :param y: Latitude degrees
    :return: The nearest node value and associated triangle.
    """
    global _local
    ensure_bathymetry_index()
    triangle, n1, n2, n3 = list(_local.index.nearest((x,y), objects=True))[0].object
    var = DataArray.objects.filter(basename=basename, name=varname, time__lte=time).order_by('-version')
    if version:
        var = var.filter(version=version)
    if var:
        var=var.first()
        var = pickle.loads(var.data)
        return triangle, var[n1] or var[n2] or var[n3] # TODO find the nearest non-null value as opposed to just picking one.
    else:
        raise KeyError()
