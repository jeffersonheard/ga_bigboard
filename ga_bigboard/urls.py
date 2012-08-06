from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from ga_bigboard.api import api_v4
from ga_bigboard import views
from django.contrib.auth.views import login

urlpatterns = patterns('',
    url(r'^api/', include(api_v4.urls)),
    url(r'^login/', login, kwargs={'template_name' : 'ga_bigboard/login.template.html'}, name='bigboard-login'),
    url(r'^room/', views.RoomView.as_view(), name='bigboard-room'),
    url(r'^$', views.RoomListView.as_view(), name='bigboard-room-list'),
    url(r'^create_room/', views.CreateRoomView.as_view(success_url=reverse_lazy('bigboard-room')), name='bigboard-create-room'),
    url(r'^join/', views.JoinView.as_view(), name='bigboard-join'),
    url(r'^leave/', views.LeaveView.as_view(), name='bigboard-leave'),
    url(r'^heartbeat/', views.HeartbeatView.as_view(), name='bigboard-heartbeat'),
    url(r'^center/', views.RecenterView.as_view(), name='bigboard-center'),
    #url(r'^admin',views.TastypieAdminView.as_view(), name='ga_bigboard_admin'),

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
