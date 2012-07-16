# Create your views here.

from ga_ows.rendering.palettes import _Palette, LinearGradient, ColorBin, CatchAll, rgba
from ga_ows.views import wms
from osr import SpatialReference, CoordinateTransformation
import numpy as np
import cairo as cr
from datetime import datetime
from logging import getLogger

from cera import query, models

log = getLogger(__name__)

def jet(mn, mx):
    """MATLAB jet colormap gradient spread from a min value to a max value"""
    delta = (mx-mn) / 32.0
    return _Palette(
        ColorBin(rgba(1,1,1,0), mn-10, mn, include_right=True),
        LinearGradient(rgba(  0,  0,143), rgba(  0,  0,175), mn +  0*delta, mn +  1*delta, include_left=False, include_right=False),
        LinearGradient(rgba(  0,  0,175), rgba(  0,  0,207), mn +  1*delta, mn +  2*delta, include_right=False),
        LinearGradient(rgba(  0,  0,207), rgba(  0,  0,239), mn +  2*delta, mn +  3*delta, include_right=False),
        LinearGradient(rgba(  0,  0,239), rgba(  0, 16,255), mn +  3*delta, mn +  4*delta, include_right=False),
        LinearGradient(rgba(  0, 16,255), rgba(  0, 48,255), mn +  4*delta, mn +  5*delta, include_right=False),
        LinearGradient(rgba(  0, 48,255), rgba(  0, 80,255), mn +  5*delta, mn +  6*delta, include_right=False),
        LinearGradient(rgba(  0, 80,255), rgba(  0,112,255), mn +  6*delta, mn +  7*delta, include_right=False),
        LinearGradient(rgba(  0,112,255), rgba(  0,143,255), mn +  7*delta, mn +  8*delta, include_right=False),
        LinearGradient(rgba(  0,143,255), rgba(  0,175,255), mn +  8*delta, mn +  9*delta, include_right=False),
        LinearGradient(rgba(  0,175,255), rgba(  0,207,255), mn +  9*delta, mn + 10*delta, include_right=False),
        LinearGradient(rgba(  0,207,255), rgba(  0,239,255), mn + 10*delta, mn + 11*delta, include_right=False),
        LinearGradient(rgba(  0,239,255), rgba( 16,255,239), mn + 11*delta, mn + 12*delta, include_right=False),
        LinearGradient(rgba( 16,255,239), rgba( 48,255,207), mn + 12*delta, mn + 13*delta, include_right=False),
        LinearGradient(rgba( 48,255,207), rgba( 80,255,175), mn + 13*delta, mn + 14*delta, include_right=False),
        LinearGradient(rgba( 80,255,175), rgba(112,255,143), mn + 14*delta, mn + 15*delta, include_right=False),
        LinearGradient(rgba(112,255,143), rgba(143,255,112), mn + 15*delta, mn + 16*delta, include_right=False),
        LinearGradient(rgba(143,255,112), rgba(175,255, 80), mn + 16*delta, mn + 17*delta, include_right=False),
        LinearGradient(rgba(175,255, 80), rgba(207,255, 48), mn + 17*delta, mn + 18*delta, include_right=False),
        LinearGradient(rgba(207,255, 48), rgba(239,255, 16), mn + 18*delta, mn + 19*delta, include_right=False),
        LinearGradient(rgba(239,255, 16), rgba(255,239,  0), mn + 19*delta, mn + 20*delta, include_right=False),
        LinearGradient(rgba(255,239,  0), rgba(255,207,  0), mn + 20*delta, mn + 21*delta, include_right=False),
        LinearGradient(rgba(255,207,  0), rgba(255,175,  0), mn + 21*delta, mn + 22*delta, include_right=False),
        LinearGradient(rgba(255,175,  0), rgba(255,143,  0), mn + 22*delta, mn + 23*delta, include_right=False),
        LinearGradient(rgba(255,143,  0), rgba(255,112,  0), mn + 23*delta, mn + 24*delta, include_right=False),
        LinearGradient(rgba(255,112,  0), rgba(255, 80,  0), mn + 24*delta, mn + 25*delta, include_right=False),
        LinearGradient(rgba(255, 80,  0), rgba(255, 48,  0), mn + 25*delta, mn + 26*delta, include_right=False),
        LinearGradient(rgba(255, 48,  0), rgba(255, 16,  0), mn + 26*delta, mn + 27*delta, include_right=False),
        LinearGradient(rgba(255, 16,  0), rgba(239,  0,  0), mn + 27*delta, mn + 28*delta, include_right=False),
        LinearGradient(rgba(239,  0,  0), rgba(207,  0,  0), mn + 28*delta, mn + 29*delta, include_right=False),
        LinearGradient(rgba(207,  0,  0), rgba(175,  0,  0), mn + 29*delta, mn + 30*delta, include_right=False),
        LinearGradient(rgba(175,  0,  0), rgba(143,  0,  0), mn + 30*delta, mn + 31*delta, include_right=False),
        ColorBin      (rgba(143,  0,  0), mn+31*delta, mx),
        CatchAll      (rgba(  1,  1,  1,  0))
    )

# color palettes for the views based on CERA NetCDFs
imperial = dict(
    water_height = jet(0, 10),
    inundation_depth = jet(0, 6),
    wave_height = jet(0, 26),
    rel_peak = jet(0, 16),
    wind_speed = jet(0, 60),
)

default = jet(0.0, 128)

metric = dict(
    water_height = (default, 0, 3),
    inundation_depth = (default, 0, 2),
    wave_height = (default, 0, 8),
    rel_peak = (default, 0, 16),
    wind_speed = (default, 0, 100),
)

imperial_units = ('ft','ft','ft','s','mph')
metric_units = ('m','m','m','s','km/h')

palettes = {
    'default' : jet(0.0, 128.0),
    'adcirc' :  jet(0.0, 128.0)
}


class RenderingContext(object):
    """Renders a triangular irregular grid to a Cairo surface"""

    def __init__(self, palette, minx, miny, maxx, maxy, minv, maxv, width, height, surfdata=None):
        """
        :param palette: the palette to use to color the geometry
        :param minx: the minx to render in the geometry's coordinate system
        :param miny: the miny to render
        :param maxx: the maxx to render
        :param maxy: the maxy to render
        :param width: the width of the image in pixels
        :param height: the height of the image in pixels
        :param surfdata: if we have pre-rendered surface data (like another layer), pass it in so a new surface isn't created.
        :return:
        """
        self.palette = palette

        self.minx=minx
        self.miny=miny
        self.maxx=maxx
        self.maxy=maxy
        self.minv=minv
        self.maxv=maxv

        if surfdata:
            self.surface = cr.ImageSurface.create_for_data(surfdata, cr.FORMAT_ARGB32, width, height)
        else:
            self.surface = cr.ImageSurface(cr.FORMAT_ARGB32, width, height)
        self.ctx = cr.Context(self.surface)
 
        self.height = height
        self.pixel_w = (maxx-minx) / width
        self.pixel_h = (maxy-miny) / height

    def cleanslate(self):
        """Clear the slate for new rendering.
        """
        self.ctx.set_source_rgba(1,1,1,0)
        self.ctx.set_operator(cr.OPERATOR_SOURCE)
        self.ctx.paint()

    def render(self, geometry, data):
        """
        :param data: The data to use.  This will be passed to the styler wholesale.
        :return: None
        """
        c = 0
        binsize=(self.maxv-self.minv)/128.0
        bins = np.arange(self.minv, self.maxv, binsize)
        data = np.digitize(np.clip(data, self.minv, self.maxv,data), bins)

        geometry[...,...,0] -= self.minx
        geometry[...,...,0] /= self.pixel_w
        geometry[...,...,1] -= self.maxy
        geometry[...,...,1] /= -self.pixel_h

        then = datetime.now()
        last_bin = None
        for i in np.argsort(data):
            c+=1

            if last_bin is None:
                    color = np.array([self.palette(data[i])], dtype=np.uint32).view(dtype=np.uint8) / 255.0
                    self.ctx.set_source_rgba(*color)
                    last_bin = data[i]
            elif last_bin != data[i]:
                    self.ctx.fill()
                    color = np.array([self.palette(data[i])], dtype=np.uint32).view(dtype=np.uint8) / 255.0
                    self.ctx.set_source_rgba(*color)
                    last_bin = data[i]
            self._sketch_triangle(geometry[i])

        self.ctx.fill()
        delta = datetime.now() - then # timing
        log.debug("Rendered {ln} elements in {secs}.{usecs}".format(ln=c, secs=delta.seconds, usecs=delta.microseconds)) # timing

    def _sketch_triangle(self, g):
        self.ctx.move_to(*g[0])
        self.ctx.line_to(*g[1])
        self.ctx.line_to(*g[2])
        self.ctx.close_path()

# TODO create a WCS view for the local pyramid - could use OpenDAP subsetting for this.

# TODO create a WMS view for the local pyramid.

class WMSAdapter(wms.WMSAdapterBase):
    def __init__(self, styles):
        super(WMSAdapter, self).__init__({}, requires_time=True)
        self.cache = wms.WMSCache('cera')
        self.styles = styles

    def get_valid_elevations(self, **kwargs):
        return [0] # TODO get the elevations from the bathymetry and allow a person to filter based on that.

    # TODO constrain the max/mins somehow other than hardcoding them as 0, 6.0.  That's just terrible.
    def get_2d_dataset(
        self, layers, srs, bbox, width, height, styles, bgcolor, transparent, time, elevation, v, filter, **kwargs
    ):

        srs = int(srs[5:] if srs.upper().startswith('EPSG:') else int(srs))
        t_srs = SpatialReference()
        s_srs = SpatialReference()
        s_srs.ImportFromEPSG(4326)
        t_srs.ImportFromEPSG(srs)
        crx = CoordinateTransformation(t_srs, s_srs) # transform to lon-lat for getting into the bathymetry index
        x1, y1, _ = crx.TransformPoint(bbox[0], bbox[1], 0)
        x2, y2, _ = crx.TransformPoint(bbox[2], bbox[3], 0)

        t_srs = SpatialReference()
        s_srs = SpatialReference()
        s_srs.ImportFromEPSG(4326)
        t_srs.ImportFromEPSG(srs)
        xrc = CoordinateTransformation(s_srs, t_srs)

        then = datetime.now() # timing
        palette, minv, maxv = self.styles[styles]
        ctx = RenderingContext(palette, bbox[0], bbox[1], bbox[2], bbox[3], minv, maxv, width, height)
        delta = datetime.now() - then # timing
        log.debug("Created rendering context in {secs}.{usecs}".format(secs=delta.seconds, usecs=delta.microseconds)) # timing

        for layer in layers:
            basename, varname = layer.split('.')
            then = datetime.now()
            geometry, values = query.bbox_mean_values_for_triangles(basename, varname, time, (x1,y1,x2,y2))
            delta = datetime.now() - then # timing
            log.debug("query completed in {secs}.{usecs}".format(secs=delta.seconds, usecs=delta.microseconds)) # timing
            if geometry.shape[0] == 0:
               continue
            then = datetime.now()
            if srs != 4326:
                log.debug('transforming geometry from 4326 to {srs}'.format(srs=srs))
                geometry = geometry.reshape(geometry.shape[0]*3, 2)
                for i in range(geometry.shape[0]):
                    x, y, _ = xrc.TransformPoint(geometry[i,0], geometry[i,1])
                    geometry[i,0] = x
                    geometry[i,1] = y
                geometry = geometry.reshape(geometry.shape[0]/3, 3, 2)
            delta = datetime.now() - then # timing
            log.debug("transformation completed in {secs}.{usecs}".format(secs=delta.seconds, usecs=delta.microseconds)) # timing

            ctx.render(geometry, values)

        return ctx.surface

    def get_layer_descriptions(self):
        query.ensure_bathymetry_index()
        minx, miny, maxx, maxy = query._index.bounds
        return [{
            'name' : var.basename + '.' + var.name,
            'srs' : 4326,
            'queryable' : True,
            'minx' : minx,
            'miny' : miny,
            'maxx' : maxx,
            'maxy' : maxy,
            'll_minx' : minx,
            'll_miny' : miny,
            'll_maxx' : maxx,
            'll_maxy' : maxy,
            'styles' : self.styles.keys()

        } for var in models.Variable.objects.all()]

    def cache_result(self, item, **kwargs):
        locator = kwargs
        locator['layers'] = ','.join(locator['layers'])
        locator['time'] = locator['time'].strftime("%Y%m%d%H")
        if 'fresh' in locator:
            del locator['fresh']

        self.cache.save(item, **locator)

    def get_cache_record(self, **kwargs):
        locator = kwargs
        locator['layers'] = ','.join(locator['layers'])
        locator['time'] = locator['time'].strftime("%Y%m%d%H")
        if 'fresh' in locator:
            del locator['fresh']


        return self.cache.locate(**locator)

    def get_valid_times(self, **kwargs):
        return [run.when for run in models.ModelRun.objects.all()] # TODO this should contain all valid times for each layer, not just the model run times.

    def nativesrs(self, layer):
        return 4326

    def get_valid_versions(self, group_by=None, **kwargs):
        return [run.when.strftime('%Y%m%d%H') for run in models.ModelRun.objects.all()]

    def get_feature_info(self, wherex, wherey, layers, callback, format, feature_count, srs, filter):
        srs = int(srs[5:] if srs.upper().startswith('EPSG:') else srs)
        t_srs = SpatialReference()
        s_srs = SpatialReference()
        s_srs.ImportFromEPSG(4326)
        t_srs.ImportFromEPSG(srs)
        crx = CoordinateTransformation(t_srs, s_srs) # transform to lon-lat for getting into the bathymetry index
        x, y, _ = crx.TransformPoint(wherex, wherey, 0)

        result = {}
        for layer in layers:
            basename, varname = layer.split('.')
            triangle, value = query.value_nearest(basename, varname, filter['time'], x, y, version=filter['version'] if 'version' in filter else None)
            result[layer] = value

        if callback:
            return callback(result)
        else:
            return result

    def nativebbox(self):
        query.ensure_bathymetry_index()
        return query._index.bounds

    def layerlist(self):
        return [(var.basename + '.' + var.name) for var in models.Variable.objects.all()]

class WMS(wms.WMS):
    adapter = WMSAdapter(metric)
    title = "NCFS ADCIRC storm surge model output"

