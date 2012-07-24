# Create your views here.
import datetime
from django.contrib.gis.geos.point import Point
from django.core import serializers
from django.http import HttpResponseForbidden, HttpResponse
from django.views import generic as dv
from django.contrib import auth
import json
from bson import json_util
from ga_bigboard import models

class RoomView(dv.TemplateView):
    template_name = 'ga_bigboard/room.template.html'

    def get_context_data(self, **kwargs):
        kwargs['rooms'] = models.Room.objects.all()
        return kwargs


class TastypieAdminView(dv.TemplateView):
    template_name = 'ga_bigboard/tastyadmin.html'

class JoinView(dv.View):
    def get(self, request, *args, **kwargs):
        logged_in = not request.user.is_anonymous()
        user = request.user

        if request.user.is_anonymous or (request.GET['username'] and request.user.username != request.GET['username']):
            username = request.GET['username']
            password = request.GET['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                logged_in = True

        if not logged_in:
            return HttpResponseForbidden()
        else:
            room = request.GET['room']
            room = models.Room.objects.get(name=room)

            # remove the participant upon rejoining to prevent one user from logging in multiple places as a single participant.
            if models.Participant.objects.filter(room=room, user=user).count() != 0:
                models.Participant.objects.filter(room=room, user=user).delete()

            participant = models.Participant.objects.create(
                user=user,
                where=Point(0, 0, srid=4326),
                room=room
            )
            participant.roles.add(*models.Role.objects.filter(users=user))

            request.session['room'] = room
            request.session['participant'] = participant

            return HttpResponse(json.dumps({
                "user_id" : user.pk,
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
            request.session.flush()

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

