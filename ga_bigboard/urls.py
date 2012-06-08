from django.conf.urls.defaults import patterns, include, url
from ga_bigboard.api import api_v4
from django.views.generic import TemplateView
from ga_bigboard import views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin

urlpatterns = patterns('',
    url(r'^', include(api_v4.urls)),
    url(r'^room', views.RoomView.as_view()),
    url(r'^join', views.JoinView.as_view()),
    url(r'^leave', views.LeaveView.as_view()),
    url(r'^heartbeat', views.HeartbeatView.as_view()),
    url(r'^center', views.RecenterView.as_view()),
    url(r'^admin',views.TastypieAdminView.as_view()),

    # Examples:
    # url(r'^$', 'ga.views.home', name='home'),
    # url(r'^ga/', include('ga.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
