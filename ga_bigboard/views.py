# Create your views here.
import datetime
from django.contrib.gis.geos.point import Point
from django.core import serializers
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.views import generic as dv
from django.contrib import auth
import json
from bson import json_util
from ga_bigboard import models, app_settings
from django.conf import settings
from django.core.urlresolvers import reverse
from django import forms
from tastypie.models import ApiKey

class RoomView(dv.TemplateView):
    template_name = 'ga_bigboard/room.template.html'

    def get_context_data(self, **kwargs):
        kwargs['rooms'] = models.Room.objects.all()
        if 'room' in self.request.REQUEST:
            kwargs['room'] = self.request.REQUEST['room']
        kwargs['custom_controls'] = []
        kwargs['api_key'] = self.request.user.api_key
        kwargs['username'] = self.request.user.username
        return kwargs

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            if hasattr(app_settings, 'USE_ALT_LOGIN') and app_settings.USE_ALT_LOGIN:
                return HttpResponseRedirect(reverse('bigboard-login'))
            elif hasattr(settings, "LOGIN_URL"):
                return HttpResponseRedirect(settings.LOGIN_URL)
            else:
                return HttpResponseForbidden()
        else:
            return super(RoomView, self).get(request, *args, **kwargs)


class RoomForm(forms.ModelForm):
    class Meta:
        model = models.Room
        widgets = {
            'owner' : forms.HiddenInput(),
            'roles' : forms.SelectMultiple(attrs={'data-native-menu' : 'false' })
        }

class RoomListView(dv.TemplateView):
    template_name = 'ga_bigboard/room_list.template.html'

    def get_context_data(self, **kwargs):
        kwargs['rooms'] = sorted(list(reduce(set.union, [set(r.room_set.all()[:]) for r in self.request.user.role_set.all()])))
        kwargs['form'] = RoomForm(initial={
            'owner' : 1
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            if hasattr(app_settings, 'USE_ALT_LOGIN') and app_settings.USE_ALT_LOGIN:
                return HttpResponseRedirect(reverse('bigboard-login'))
            elif hasattr(settings, "LOGIN_URL"):
                return HttpResponseRedirect(settings.LOGIN_URL)
            else:
                return HttpResponseForbidden()
        else:
            return super(RoomListView, self).get(request, *args, **kwargs)


class CreateRoomView(dv.CreateView):
    template_name = 'ga_bigboard/create_room.template.html'
    form_class = RoomForm

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse('bigboard-room-list'))

    def form_valid(self, form):
        self.success_url = reverse('bigboard-room') + "?room=" + form.cleaned_data['name']
        return super(CreateRoomView, self).form_valid(form)


class TastypieAdminView(dv.TemplateView):
    template_name = 'ga_bigboard/tastyadmin.html'

class JoinView(dv.View):
    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            if hasattr(app_settings, 'USE_ALT_LOGIN') and app_settings.USE_ALT_LOGIN:
                return HttpResponseRedirect(reverse('bigboard-login'))
            elif hasattr(settings, "LOGIN_URL"):
                return HttpResponseRedirect(settings.LOGIN_URL)
            else:
                return HttpResponseForbidden()
        else:
            room = request.GET['room']
            room = models.Room.objects.get(name=room)

            # remove the participant upon rejoining to prevent one user from logging in multiple places as a single participant.
            if models.Participant.objects.filter(room=room, user=request.user).count() != 0:
                models.Participant.objects.filter(room=room, user=request.user).delete()

            participant = models.Participant.objects.create(
                user=request.user,
                where=Point(0, 0, srid=4326),
                room=room
            )
            participant.roles.add(*models.Role.objects.filter(users=request.user))

            request.session['room'] = room
            request.session['participant'] = participant

            return HttpResponse(json.dumps({
                "user_id" : request.user.pk,
                "room" : serializers.serialize('json', [room]),
            }, default=json_util.default), mimetype='application/json')

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

class LeaveView(dv.View):
    def get(self, request, *args, **kwargs):
        logged_in = not request.user.is_anonymous() and 'participant' in request.session

        if logged_in:
            request.session['participant'].delete()
            del request.session['participant']
            del request.session['room']

            return HttpResponse(json.dumps({"ok" : True}), mimetype='application/json')
        else:
            return HttpResponseForbidden('user not logged in')

class HeartbeatView(dv.View):
    def get(self, request, *args, **kwargs):

        if request.user != request.session['participant'].user:
            return HttpResponseForbidden()

        request.session['participant'].where = Point(float(request.GET['x']), float(request.GET['y']), srid=4326)
        request.session['participant'].last_heartbeat = datetime.datetime.utcnow()
        request.session['participant'].save()
        request.session['participant'] = models.Participant.objects.get(pk=request.session['participant'].pk)

        return HttpResponse()

class RecenterView(dv.View):
    def get(self, request, *args, **kwargs):
        if request.user != request.session['participant'].user:
            return HttpResponseForbidden()

        request.session['room'].center = Point(float(request.GET['x']), float(request.GET['y']), srid=4326)
        request.session['room'].zoom_level = int(request.GET['z'])
        request.session['room'].save()
        request.session['room'] = models.Room.objects.get(pk=request.session['room'].pk)

        return HttpResponse()

