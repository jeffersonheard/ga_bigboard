from django.contrib.gis import admin
from ga_bigboard import models

admin.site.register(models.Annotation, admin_class=admin.OSMGeoAdmin)
admin.site.register(models.Role)
admin.site.register(models.Participant, admin_class=admin.OSMGeoAdmin)
admin.site.register(models.Chat, admin_class=admin.OSMGeoAdmin)
admin.site.register(models.Room, admin_class=admin.OSMGeoAdmin)
admin.site.register(models.CustomControl)
admin.site.register(models.SharedOverlay)
admin.site.register(models.Overlay)

admin.site.register(models.PersonalView, admin_class=admin.OSMGeoAdmin)
admin.site.register(models.BBNotification, admin_class=admin.OSMGeoAdmin)

