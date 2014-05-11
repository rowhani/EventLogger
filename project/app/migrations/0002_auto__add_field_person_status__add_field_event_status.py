# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Person.status'
        db.add_column('Person', 'status',
                      self.gf('django.db.models.fields.CharField')(default='public', max_length=15, blank=True),
                      keep_default=False)

        # Adding field 'Event.status'
        db.add_column('Event', 'status',
                      self.gf('django.db.models.fields.CharField')(default='public', max_length=15, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Person.status'
        db.delete_column('Person', 'status')

        # Deleting field 'Event.status'
        db.delete_column('Event', 'status')


    models = {
        u'app.attachment': {
            'Meta': {'object_name': 'Attachment', 'db_table': "'Attachment'"},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': u"orm['app.Event']"}),
            'filename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'app.event': {
            'Meta': {'object_name': 'Event', 'db_table': "'Event'"},
            'actions_taken': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_happened': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'persons': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'events'", 'to': u"orm['app.Person']", 'db_table': "'Event_Person'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'photo': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'related_events': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_events_rel_+'", 'null': 'True', 'db_table': "'Event_Event'", 'to': u"orm['app.Event']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '15', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'events'", 'to': u"orm['app.Tag']", 'db_table': "'Event_Tag'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'app.person': {
            'Meta': {'object_name': 'Person', 'db_table': "'Person'"},
            'birth_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'birth_place': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'death_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'death_place': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'person_photo': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '15', 'blank': 'True'})
        },
        u'app.tag': {
            'Meta': {'object_name': 'Tag', 'db_table': "'Tag'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['app']