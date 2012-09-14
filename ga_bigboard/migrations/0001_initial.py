# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.contrib.gis.geos import Point


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Role'
        db.create_table('ga_bigboard_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('self_assignable', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ga_bigboard', ['Role'])

        # Adding M2M table for field users on 'Role'
        db.create_table('ga_bigboard_role_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm['ga_bigboard.role'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('ga_bigboard_role_users', ['role_id', 'user_id'])

        # Adding model 'Overlay'
        db.create_table('ga_bigboard_overlay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('default_creation_options', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('ga_bigboard', ['Overlay'])

        # Adding M2M table for field roles on 'Overlay'
        db.create_table('ga_bigboard_overlay_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('overlay', models.ForeignKey(orm['ga_bigboard.overlay'], null=False)),
            ('role', models.ForeignKey(orm['ga_bigboard.role'], null=False))
        ))
        db.create_unique('ga_bigboard_overlay_roles', ['overlay_id', 'role_id'])

        # Adding model 'CustomControl'
        db.create_table('ga_bigboard_customcontrol', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
        ))
        db.send_create_signal('ga_bigboard', ['CustomControl'])

        # Adding M2M table for field roles on 'CustomControl'
        db.create_table('ga_bigboard_customcontrol_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customcontrol', models.ForeignKey(orm['ga_bigboard.customcontrol'], null=False)),
            ('role', models.ForeignKey(orm['ga_bigboard.role'], null=False))
        ))
        db.create_unique('ga_bigboard_customcontrol_roles', ['customcontrol_id', 'role_id'])

        # Adding model 'Room'
        db.create_table('ga_bigboard_room', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('base_layer_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('base_layer_wms', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_bigboard.Overlay'], null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('center', self.gf('django.contrib.gis.db.models.fields.PointField')(default=Point(0,0), srid=3857)),
            ('zoom_level', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal('ga_bigboard', ['Room'])

        # Adding M2M table for field roles on 'Room'
        db.create_table('ga_bigboard_room_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('room', models.ForeignKey(orm['ga_bigboard.room'], null=False)),
            ('role', models.ForeignKey(orm['ga_bigboard.role'], null=False))
        ))
        db.create_unique('ga_bigboard_room_roles', ['room_id', 'role_id'])

        # Adding model 'SharedOverlay'
        db.create_table('ga_bigboard_sharedoverlay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('overlay', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_bigboard.Overlay'])),
            ('sharing_options', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('shared_with_all', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_bigboard.Room'])),
        ))
        db.send_create_signal('ga_bigboard', ['SharedOverlay'])

        # Adding M2M table for field shared_with_users on 'SharedOverlay'
        db.create_table('ga_bigboard_sharedoverlay_shared_with_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sharedoverlay', models.ForeignKey(orm['ga_bigboard.sharedoverlay'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('ga_bigboard_sharedoverlay_shared_with_users', ['sharedoverlay_id', 'user_id'])

        # Adding M2M table for field shared_with_roles on 'SharedOverlay'
        db.create_table('ga_bigboard_sharedoverlay_shared_with_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sharedoverlay', models.ForeignKey(orm['ga_bigboard.sharedoverlay'], null=False)),
            ('role', models.ForeignKey(orm['ga_bigboard.role'], null=False))
        ))
        db.create_unique('ga_bigboard_sharedoverlay_shared_with_roles', ['sharedoverlay_id', 'role_id'])

        # Adding model 'Participant'
        db.create_table('ga_bigboard_participant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('where', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True)),
            ('last_heartbeat', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_bigboard.Room'])),
        ))
        db.send_create_signal('ga_bigboard', ['Participant'])

        # Adding M2M table for field roles on 'Participant'
        db.create_table('ga_bigboard_participant_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('participant', models.ForeignKey(orm['ga_bigboard.participant'], null=False)),
            ('role', models.ForeignKey(orm['ga_bigboard.role'], null=False))
        ))
        db.create_unique('ga_bigboard_participant_roles', ['participant_id', 'role_id'])

        # Adding model 'Annotation'
        db.create_table('ga_bigboard_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_bigboard.Room'])),
            ('associated_overlay', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=32, null=True, blank=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.GeometryField')(srid=3857)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('audio', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('video', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('media', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ga_bigboard', ['Annotation'])

        # Adding model 'Chat'
        db.create_table('ga_bigboard_chat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_bigboard.Room'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('where', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('ga_bigboard', ['Chat'])

        # Adding M2M table for field at on 'Chat'
        db.create_table('ga_bigboard_chat_at', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('chat', models.ForeignKey(orm['ga_bigboard.chat'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('ga_bigboard_chat_at', ['chat_id', 'user_id'])

        # Adding model 'PersonalView'
        db.create_table('ga_bigboard_personalview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_bigboard.Room'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('where', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('zoom_level', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('ga_bigboard', ['PersonalView'])

        # Adding model 'BBNotification'
        db.create_table('ga_bigboard_bbnotification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_bigboard.Room'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('shared_with_all', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('where', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('zoom_level', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('ga_bigboard', ['BBNotification'])

        # Adding M2M table for field shared_with_roles on 'BBNotification'
        db.create_table('ga_bigboard_bbnotification_shared_with_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bbnotification', models.ForeignKey(orm['ga_bigboard.bbnotification'], null=False)),
            ('role', models.ForeignKey(orm['ga_bigboard.role'], null=False))
        ))
        db.create_unique('ga_bigboard_bbnotification_shared_with_roles', ['bbnotification_id', 'role_id'])


    def backwards(self, orm):
        # Deleting model 'Role'
        db.delete_table('ga_bigboard_role')

        # Removing M2M table for field users on 'Role'
        db.delete_table('ga_bigboard_role_users')

        # Deleting model 'Overlay'
        db.delete_table('ga_bigboard_overlay')

        # Removing M2M table for field roles on 'Overlay'
        db.delete_table('ga_bigboard_overlay_roles')

        # Deleting model 'CustomControl'
        db.delete_table('ga_bigboard_customcontrol')

        # Removing M2M table for field roles on 'CustomControl'
        db.delete_table('ga_bigboard_customcontrol_roles')

        # Deleting model 'Room'
        db.delete_table('ga_bigboard_room')

        # Removing M2M table for field roles on 'Room'
        db.delete_table('ga_bigboard_room_roles')

        # Deleting model 'SharedOverlay'
        db.delete_table('ga_bigboard_sharedoverlay')

        # Removing M2M table for field shared_with_users on 'SharedOverlay'
        db.delete_table('ga_bigboard_sharedoverlay_shared_with_users')

        # Removing M2M table for field shared_with_roles on 'SharedOverlay'
        db.delete_table('ga_bigboard_sharedoverlay_shared_with_roles')

        # Deleting model 'Participant'
        db.delete_table('ga_bigboard_participant')

        # Removing M2M table for field roles on 'Participant'
        db.delete_table('ga_bigboard_participant_roles')

        # Deleting model 'Annotation'
        db.delete_table('ga_bigboard_annotation')

        # Deleting model 'Chat'
        db.delete_table('ga_bigboard_chat')

        # Removing M2M table for field at on 'Chat'
        db.delete_table('ga_bigboard_chat_at')

        # Deleting model 'PersonalView'
        db.delete_table('ga_bigboard_personalview')

        # Deleting model 'BBNotification'
        db.delete_table('ga_bigboard_bbnotification')

        # Removing M2M table for field shared_with_roles on 'BBNotification'
        db.delete_table('ga_bigboard_bbnotification_shared_with_roles')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ga_bigboard.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'associated_overlay': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'audio': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '3857'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'media': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_bigboard.Room']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ga_bigboard.bbnotification': {
            'Meta': {'ordering': "['when']", 'object_name': 'BBNotification'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_bigboard.Room']"}),
            'shared_with_all': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'shared_with_roles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ga_bigboard.Role']", 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'where': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'zoom_level': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'ga_bigboard.chat': {
            'Meta': {'ordering': "['when']", 'object_name': 'Chat'},
            'at': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'at'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_bigboard.Room']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'where': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'})
        },
        'ga_bigboard.customcontrol': {
            'Meta': {'object_name': 'CustomControl'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ga_bigboard.Role']", 'symmetrical': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'ga_bigboard.overlay': {
            'Meta': {'object_name': 'Overlay'},
            'default_creation_options': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ga_bigboard.Role']", 'symmetrical': 'False'})
        },
        'ga_bigboard.participant': {
            'Meta': {'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_heartbeat': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ga_bigboard.Role']", 'symmetrical': 'False'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_bigboard.Room']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'where': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'})
        },
        'ga_bigboard.personalview': {
            'Meta': {'ordering': "['when']", 'object_name': 'PersonalView'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_bigboard.Room']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'where': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'zoom_level': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'ga_bigboard.role': {
            'Meta': {'object_name': 'Role'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'self_assignable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        'ga_bigboard.room': {
            'Meta': {'object_name': 'Room'},
            'base_layer_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'base_layer_wms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_bigboard.Overlay']", 'null': 'True', 'blank': 'True'}),
            'center': ('django.contrib.gis.db.models.fields.PointField', [], {'default': '<Point object at 0x10defdac0>', 'srid': '3857'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ga_bigboard.Role']", 'symmetrical': 'False'}),
            'zoom_level': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'ga_bigboard.sharedoverlay': {
            'Meta': {'object_name': 'SharedOverlay'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_bigboard.Overlay']"}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_bigboard.Room']"}),
            'shared_with_all': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'shared_with_roles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ga_bigboard.Role']", 'null': 'True', 'blank': 'True'}),
            'shared_with_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'sharing_options': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['ga_bigboard']