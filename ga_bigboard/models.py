from django.contrib.gis.db import models as m
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User

class Role(m.Model):
    #: the role name
    name = m.CharField(max_length=255, unique=True, blank=False, db_index=True)

    #: a human readable name to the role.
    verbose_name = m.CharField(max_length=255, unique=True, blank=False, db_index=True)

    #: a longer text description of the role
    description = m.TextField(blank=True)

    #: all the users associated with the role
    users = m.ManyToManyField(User)

    self_assignable = m.BooleanField(default=False)

    objects = m.GeoManager()

    def __unicode__(self):
        return self.verbose_name if self.verbose_name else self.name

class Overlay(m.Model):
    """An OpenLayers overlay."""

    #: should be a valid OpenLayers.Layer.* type in OpenLayers
    kind = m.CharField(max_length=64, blank=False, choices=(
        ('WMS','Web Map Service'),
        ('WFS','Web Feature Service'),
        ('GeoJSON', 'GeoJSON Feed')
    ))

    #: the layer name
    name = m.CharField(max_length=255, blank=False, db_index=True, unique=True)

    #: description
    description = m.TextField()

    #: Creation options for the layer
    default_creation_options = m.TextField()

    #: Who is this overlay visible to?
    roles = m.ManyToManyField(Role) # names

    objects = m.GeoManager()

    def __unicode__(self):
        return self.name

class CustomControl(m.Model):
    #: the url of the custom control
    url = m.URLField(blank=False)

    #: the name of the custom control
    name = m.CharField(max_length=255, blank=False, db_index=True, unique=True)

    #: the roles that the custom control is visible by
    roles = m.ManyToManyField(Role)

    objects = m.GeoManager()

    def __unicode__(self):
        return self.name

class Room(m.Model):
    """A conference room"""

    #: The room name
    name = m.CharField(max_length=255, blank=False, db_index=True, unique=True)

    #: The room's base layer type. Should be "Google", "Bing", "OSM", or "WMS"
    base_layer_type = m.CharField(max_length=32, choices=(
        ('GoogleTerrain','Google Terrain'),
        ('GoogleHybrid','Google Streets'),
        ('GoogleSatellite','Google Satellite'),
        ('OSM','Open Streetmap'),
        ('WMS','WMS')
    ))

    #: Base layer, if WMS.
    base_layer_wms = m.ForeignKey(Overlay, null=True, db_index=True, blank=True)

    #: A user's primary key.
    owner = m.ForeignKey(User, db_index=True)

    #: The roles allowed to join this room.
    roles = m.ManyToManyField(Role)

    #: The center of the room when the user first logs in.
    center = m.PointField(srid=3857, default=Point(0,0,srid=4326))

    #: The zoom level of this room when the user first logs in
    zoom_level = m.IntegerField(default=5, null=False)

    objects = m.GeoManager()

    def __unicode__(self):
        return self.name

class SharedOverlay(m.Model):
    """An overlay that is shared"""

    overlay = m.ForeignKey(Overlay)

    #: "overlay" the options in the original with this to get the options that should be set by default for sharing
    sharing_options = m.TextField(blank=True)

    #: User ids that the layer is shared with
    shared_with_users = m.ManyToManyField(User, blank=True, null=True)

    #: Roles that the layer is shared with
    shared_with_roles = m.ManyToManyField(Role, blank=True, null=True)

    #: Share with all?
    shared_with_all = m.BooleanField(default=True)

    #: which room is it attached to
    room = m.ForeignKey(Room, db_index=True)

    objects = m.GeoManager()

    def __unicode__(self):
        return self.overlay.name


class Participant(m.Model):
    """A room participant
    """

    #: the user id
    user = m.ForeignKey(User)

    #: the roles assigned to the user (by name)
    roles = m.ManyToManyField(Role)

    #: where the user currently is
    where = m.PointField(srid=4326, null=True)

    #: when the user's device last checked in
    last_heartbeat = m.DateTimeField(auto_now_add=True)

    room = m.ForeignKey(Room, db_index=True)

    objects = m.GeoManager()

    def __unicode__(self):
        return self.user.username + ' in ' + self.room.name


class Annotation(m.Model):
    """The annotations.  Filter by room and associated overlay to get the actual layer you want.  There should be a GeoJSON API for this"""

    #: must be a valid room _id for a Room object.
    room = m.ForeignKey(Room, db_index=True)

    #: associated overlay.  A valid ObjectID for an Overlay object.  if blank, then this annotates the base layer.
    associated_overlay = m.CharField(max_length=32, db_index=True, blank=True, null=True)

    #: kind.  should be "link, image, audio, video, text, media"
    kind = m.CharField(max_length=10, choices=(('link','link'),('image','image'), ('audio','audio'),('video','video'),('text','text'),('media','media'), ('label','label')))

    #: geometry.  Geometry is recorded in map units for efficiency
    geometry = m.GeometryField(srid=3857)

    #: if kind is "link", this must not be null
    link = m.URLField(null=True, blank=True)

    #: if kind is "image" this must not be null
    image = m.ImageField(null=True, upload_to='ga_bigboard')

    #: if kind is "audio" this must not be null
    audio = m.FileField(null=True, upload_to='ga_bigboard')

    #: if kind is "video" this must not be null
    video = m.FileField(null=True, upload_to='ga_bigboard')

    #: if kind is "text", this should contain actual text
    text = m.TextField(blank=True)

    #: if kind is "media" this should contain a file
    media = m.FileField(null=True, upload_to='ga_bigboard')

    #: associated user
    user = m.ForeignKey(User)

    #: when the annotation was added to the room
    when = m.DateTimeField(auto_now=True)

    objects = m.GeoManager()

    def __unicode__(self):
        return self.room.name + '@' + self.when.strftime('%Y-%M-%d %h:%m')


class Chat(m.Model):
    """A chat message"""

    room = m.ForeignKey(Room, db_index=True)

    #: the user originating the chat
    user = m.ForeignKey(User)

    #: was the chat a private message or global
    private = m.BooleanField(default=False)

    #: any usernames called out with @ signs
    at = m.ManyToManyField(User, related_name='at')

    #: the text
    text = m.TextField(blank=False)

    #: where the user was when s/he texted.
    where = m.PointField(srid=4326, null=True)

    #: when the user chatted
    when = m.DateTimeField(auto_now_add=True, db_index=True)

    def __unicode__(self):
        return self.room.name + '.' + self.user.username + '@' + self.when.strftime('%Y-%M-%d %h:%m')

    objects = m.GeoManager()

    class Meta:
        ordering = ['when']


class PersonalView(m.Model):
    """An entry for list of interesting views stored per user per room.
    """
    room = m.ForeignKey(Room, db_index=True)
    
    #: the user to whom this item belongs
    user = m.ForeignKey(User)
    
    #: name of the location
    name = m.CharField(max_length=255, blank=False)
    
    #: optional description of the location
    description = m.TextField(blank=True)
    
    #: center of map at the desired view
    where = m.PointField(srid=4326, null=False);
    
    #: The zoom level of this view
    zoom_level = m.IntegerField(default=5, null=False)
    
    #: when this view was stored
    when = m.DateTimeField(auto_now_add=True, db_index=True)
    
    def __unicode__(self):
        return self.room.name + '.' + self.user.username + ' -> ' + self.name
    
    objects = m.GeoManager()
    
    class Meta:
        ordering = ['when']


class BBNotification(m.Model):
    """A notification for roles within a room.  Stores the user's view (center/zoom)
    upon creation with a short subject and long formattable body and a severity level.
    """
    NOTIFICATION_LEVELS = (
        ('4','Information'),
        ('3','Warning'),
        ('2','Emergency'),
        ('1','Disaster'),
    )
    
    room = m.ForeignKey(Room, db_index=True)
    
    #: the user who created this notification
    user = m.ForeignKey(User)
    
    #: Roles with whom this notification are shared
    shared_with_roles = m.ManyToManyField(Role, blank=True, null=True)

    #: Share with all?
    shared_with_all = m.BooleanField(default=True)
    
    #: notification level
    level = m.CharField(max_length=2, blank=False, choices=NOTIFICATION_LEVELS)
    
    #: subjuct of the notification
    subject = m.CharField(max_length=255, blank=False)
    
    #: body of the notification
    body = m.TextField(blank=True)
    
    #: location of the occurance
    where = m.PointField(srid=4326, null=False);
    
    #: The zoom level of this view
    zoom_level = m.IntegerField(default=5, null=False)
    
    #: when this view was stored
    when = m.DateTimeField(auto_now_add=True, db_index=True)
    
    def __unicode__(self):
        return self.room.name + '.' + self.user.username + ' -> ' + self.get_level_display()
    
    objects = m.GeoManager()
    
    class Meta:
        ordering = ['when']



from django.conf import settings

# create the notification types if the CollabNotifications is installed
if 'CollabNotifications' in settings.INSTALLED_APPS:
    from CollabNotifications.models import RegisteredNotificationType
    import datetime
    
    class BBNotificationINFORMATIONtype(RegisteredNotificationType):
        type_id = 'BBINFORMATION'       #:
        title = 'Bigboard Information'  #:
        expires = 5000                  #:
        speed = 500                     #:
    
        # deleted after 1 day
        delta = datetime.timedelta(weeks=1)
        duration = delta.days*86400 + delta.seconds     #: Deleted after 1 week
        force_acknowledgement = False   #:
    
        template = 'basic-template'     #:
        django_template = 'CollabNotifications/standardTemplates.html'  #:
        description_short = ''          #:
        description_long = ''           #:
    
    class BBNotificationWARNINGtype(RegisteredNotificationType):
        type_id = 'BBWARNING'           #:
        title = 'Bigboard Warning'      #:
        expires = 5000                  #:
        speed = 500                     #:
    
        # deleted after 1 day
        delta = datetime.timedelta(weeks=4)
        duration = delta.days*86400 + delta.seconds     #: Deleted after 4 weeks
        force_acknowledgement = False   #:
    
        template = 'basic-template'     #:
        django_template = 'CollabNotifications/standardTemplates.html'  #:
        description_short = ''          #:
        description_long = ''           #:
    
    class BBNotificationEMERGENCYtype(RegisteredNotificationType):
        type_id = 'BBEMERGENCY'         #:
        title = 'Bigboard Emergency'    #:
        expires = 0                     #:
        speed = 500                     #:
    
        duration = -1                   #: Never deleted
        force_acknowledgement = True    #:
    
        template = 'basic-template'     #:
        django_template = 'CollabNotifications/standardTemplates.html'  #:
        description_short = ''          #:
        description_long = ''           #:
    
    class BBNotificationDISASTERtype(RegisteredNotificationType):
        type_id = 'BBDISASTER'          #:
        title = 'Bigboard Disaster'     #:
        expires = 0                     #:
        speed = 500                     #:
    
        duration = -1                   #: Never deleted
        force_acknowledgement = True    #:
    
        template = 'basic-template'     #:
        django_template = 'CollabNotifications/standardTemplates.html'  #:
        description_short = ''          #:
        description_long = ''           #:
