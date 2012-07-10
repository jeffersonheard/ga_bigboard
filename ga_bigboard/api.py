from django.contrib.gis.geos.geometry import GEOSGeometry
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields as f
from tastypie.api import Api
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from ga_bigboard import models
from django.contrib.auth.models import User
from ga_ows.tastyhacks import GeoResource

class WriteOnlyMineAuthorization(Authorization):
    def __init__(self, user_getter=None):
        super(WriteOnlyMineAuthorization, self).__init__()
        self.user_getter = user_getter

    def is_authorized(self, request, object=None):
        if not object:
            return True
        elif not self.user_getter and hasattr(object, 'user'):
            return request.user == object.user
        elif not self.user_getter and hasattr(object, 'owner'):
            return request.user == object.owner
        else:
            return False

class ReadOnlyMyRoleAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(roles__users=request.user)
        else:
            return object_list.none()


class MultipartResource(object):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencoded':
            return request.POST

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)

            return data

        return super(MultipartResource, self).deserialize(request, data, format)

class UserResource(ModelResource):
    class Meta:
        authentication = BasicAuthentication()

        queryset = User.objects.all()
        allowed_methods = ('get',)
        resource_name = 'user'
        filtering = {
            'username' : ALL,
            'email' : ALL,
            'id' : ALL
            }
        excludes = ['password', 'is_superuser','is_staff','is_active']


class RoleResource(ModelResource):
    users = f.ManyToManyField(UserResource, 'users')

    class Meta:
        authentication = BasicAuthentication()
        authorization = Authorization()

        queryset = models.Role.objects.all()
        allowed_methods = ('get','post','put','delete')
        resource_name = 'role'
        filtering = {
            'id' : ALL,
            'name' : ALL,
            'users' : ALL_WITH_RELATIONS
        }

class OverlayResource(ModelResource):
    roles = f.ManyToManyField(RoleResource, 'roles')

    class Meta:
        authentication = BasicAuthentication()
        authorization = ReadOnlyMyRoleAuthorization()
        queryset = models.Overlay.objects.all()
        resource_name = 'overlay'
        allowed_methods = ('get','post','put','delete')
        filtering = {
            'name' : ALL,
            'roles' : ALL_WITH_RELATIONS
        }


class RoomResource(GeoResource):
    base_layer_wms = f.ForeignKey(to=OverlayResource, attribute='base_layer_wms', full=True, null=True)
    owner = f.ForeignKey(UserResource, 'owner')
    roles = f.ManyToManyField(RoleResource, 'roles')

    class Meta:
        authentication = BasicAuthentication()
        authorization = Authorization()
        queryset = models.Room.objects.all()
        resource_name = 'room'
        allowed_methods = ('get','post','put','delete', 'patch')
        filtering = {
            'name' : ALL,
            'owner' : ALL_WITH_RELATIONS,
            'roles' : ALL_WITH_RELATIONS
        }

    def obj_create(self, bundle, request=None, **kwargs):
        return super(RoomResource, self).obj_create(bundle, request, owner=request.user)



class AnnotationResource(MultipartResource, GeoResource):
    room = f.ForeignKey(RoomResource, 'room')
    user = f.ForeignKey(UserResource, 'user')

    class Meta:
        authentication = BasicAuthentication()
        authorization = Authorization()
        queryset = models.Annotation.objects.all()
        resource_name = 'annotation'
        allowed_methods = ('get','post','put','delete')
        filtering = {
            'room' : ALL_WITH_RELATIONS,
            'associated_overlay' : ALL,
            'geometry' : ALL
        }

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.data['geometry'] = GEOSGeometry(bundle.data['geometry'])
        return super(AnnotationResource, self).obj_create(bundle, request, user=request.user)


class SharedOverlayResource(ModelResource):
    room = f.ForeignKey(RoomResource, 'room')
    overlay = f.ForeignKey(OverlayResource, 'overlay',full=True)
    shared_with_users = f.ManyToManyField(UserResource, 'shared_with_users')
    shared_with_roles = f.ManyToManyField(RoleResource, 'shared_with_roles')

    class Meta:
        authentication = BasicAuthentication()
        authorization = Authorization()
        queryset = models.SharedOverlay.objects.all()
        resource_name = 'shared_overlay'
        allowed_methods = ('get','post','put','delete')
        filtering = {
            'overlay' : ALL_WITH_RELATIONS,
            'room' : ALL_WITH_RELATIONS,
            'shared_with_all' : ALL,
            'shared_with_users' : ALL_WITH_RELATIONS,
            'shared_with_roles' : ALL_WITH_RELATIONS
        }

class ParticipantResource(GeoResource):
    room = f.ForeignKey(to=RoomResource, attribute='room')
    user = f.ForeignKey(to=UserResource, attribute='user', full=True)
    roles = f.ManyToManyField(to=RoleResource, attribute='roles', full=True)

    class Meta:
        authentication = BasicAuthentication()
        authorization = Authorization()
        queryset = models.Participant.objects.all()
        resource_name = 'participant'
        allowed_methods = ('get','post','put','delete')
        filtering = {
            'room' : ALL_WITH_RELATIONS
        }

    def obj_create(self, bundle, request=None, **kwargs):
        return super(ParticipantResource, self).obj_create(bundle, request, user=request.user.pk)


class ChatResource(GeoResource):
    room = f.ForeignKey(to=RoomResource, attribute='room')
    user = f.ForeignKey(to=UserResource, attribute='user')
    at = f.ManyToManyField(to=UserResource, attribute='at')

    class Meta:
        authentication = BasicAuthentication()
        authorization = Authorization()
        queryset = models.Chat.objects.all()
        resource_name = 'chat'
        allowed_methods = ('get','post','put','delete')
        filtering = {
            'room' : ALL_WITH_RELATIONS,
            'when' : ALL,
            'id' : ALL
        }

    def obj_create(self, bundle, request=None, **kwargs):
        return super(ChatResource, self).obj_create(bundle, request, user=request.user)


api_v4 = Api('v4')
api_v4.register(UserResource())
api_v4.register(RoleResource())
api_v4.register(AnnotationResource())
api_v4.register(OverlayResource())
api_v4.register(SharedOverlayResource())
api_v4.register(RoomResource())
api_v4.register(ParticipantResource())
api_v4.register(ChatResource())