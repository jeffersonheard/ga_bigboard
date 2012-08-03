from django.conf.urls.defaults import patterns, include, url
from ga_bigboard.api import api_v4
from django.views.generic import TemplateView
from ga_bigboard import views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin

urlpatterns = patterns('',
    url(r'^', include(api_v4.urls)),
    url(r'^room', views.RoomView.as_view(), name='ga_bigboard_room'),
    url(r'^join', views.JoinView.as_view(), name='ga_bigboard_join'),
    url(r'^leave', views.LeaveView.as_view(), name='ga_bigboard_leave'),
    url(r'^heartbeat', views.HeartbeatView.as_view(), name='ga_bigboard_heartbeat'),
    url(r'^center', views.RecenterView.as_view(), name='ga_bigboard_center'),
    url(r'^admin',views.TastypieAdminView.as_view(), name='ga_bigboard_admin'),

    # Examples:
    # url(r'^$', 'ga.views.home', name='home'),
    # url(r'^ga/', include('ga.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

# url(r'^', include(api_v4.urls, namespace='ga_bigboard')),
# reverse('api_dispatch_list', kwargs={'resource_name':'chat','api_name':'v4'})
# {% url api_dispatch_list resource_name='chat' api_name='v4'  %}