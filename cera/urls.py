from django.conf.urls import patterns, url
from cera import views

urlpatterns = patterns('',
    # url(r'^thingie/', include(api.urls)),
    url(r'^wms/', views.WMS.as_view())
)
