# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Person.modified_by'
        db.add_column('Person', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True, default=1),
                      keep_default=False)

        # Adding field 'Event.modified_by'
        db.add_column('Event', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True, default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Person.modified_by'
        db.delete_column('Person', 'modified_by_id')

        # Deleting field 'Event.modified_by'
        db.delete_column('Event', 'modified_by_id')


    models = {
        u'app.attachment': {
            'Meta': {'ordering': "['name']", 'object_name': 'Attachment', 'db_table': "'Attachment'"},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': u"orm['app.Event']"}),
            'filename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'app.event': {
            'Meta': {'ordering': "['-date_happened', 'subject']", 'object_name': 'Event', 'db_table': "'Event'"},
            'actions_taken': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_happened': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'description_raw': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'db_index': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'persons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['app.Person']", 'null': 'True', 'db_table': "'Event_Person'", 'blank': 'True'}),
            'photo': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'related_events': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_events_rel_+'", 'null': 'True', 'db_table': "'Event_Event'", 'to': u"orm['app.Event']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '15', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'events'", 'to': u"orm['app.Tag']", 'db_table': "'Event_Tag'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'app.person': {
            'Meta': {'ordering': "['first_name', 'last_name']", 'object_name': 'Person', 'db_table': "'Person'"},
            'birth_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'birth_place': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'death_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'death_place': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['app.Event']", 'null': 'True', 'db_table': "'Event_Person'", 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'person_photo': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '15', 'blank': 'True'})
        },
        u'app.tag': {
            'Meta': {'ordering': "['name']", 'object_name': 'Tag', 'db_table': "'Tag'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']