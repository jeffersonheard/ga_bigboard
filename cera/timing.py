from osgeo import ogr
from ga_spatialnosql.index import GeoIndex
from datetime import datetime
from django.contrib.gis.geos import Polygon
from cera import query

ds3 = GeoIndex('cera/', 'bathymetry',str,int)
query.ensure_bathymetry_index()

then = datetime.now()
x1,y1,x2,y2 = -81,31,-76,36
bbox = Polygon(((x1,y1), (x2,y1), (x2,y2), (x1,y2), (x1,y1)), srid=4326)
l = ds3.bboverlaps(bbox)
fs = list(l)
delta = datetime.now()
print "finished test 1 in {secs}".format(secs=(delta-then).seconds)

then = datetime.now()
g,l = query.bbox_values_for_triangles('maxelev','inundationZeta',datetime(2012,6,28), (-81,31,-76,36))
print l.shape

delta = datetime.now()
print 'finished test 2 in {secs}'.format(secs=(delta-then).seconds)

then = datetime.now()
g, l = query.bbox_mean_values_for_triangles('maxelev','inundationZeta',datetime(2012,6,28), (-81,31,-76,36))
print l.shape
delta = datetime.now()
print 'finished test 3 in {secs}'.format(secs=(delta-then).seconds)
