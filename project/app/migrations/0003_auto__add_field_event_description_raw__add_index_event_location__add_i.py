# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field events on 'Person'
        m2m_table_name = 'Event_Person'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm[u'app.person'], null=False)),
            ('event', models.ForeignKey(orm[u'app.event'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'event_id'])

        # Adding field 'Event.description_raw'
        db.add_column('Event', 'description_raw',
                      self.gf('django.db.models.fields.TextField')(db_index=True, null=True, blank=True),
                      keep_default=False)

        # Adding index on 'Event', fields ['location']
        db.create_index('Event', ['location'])

        # Adding index on 'Event', fields ['subject']
        db.create_index('Event', ['subject'])


    def backwards(self, orm):
        # Removing index on 'Event', fields ['subject']
        db.delete_index('Event', ['subject'])

        # Removing index on 'Event', fields ['location']
        db.delete_index('Event', ['location'])

        # Removing M2M table for field events on 'Person'
        db.delete_table('Event_Person')

        # Deleting field 'Event.description_raw'
        db.delete_column('Event', 'description_raw')


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
            'description_raw': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'db_index': 'True'}),
            'persons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['app.Person']", 'null': 'True', 'db_table': "'Event_Person'", 'blank': 'True'}),
            'photo': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'related_events': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_events_rel_+'", 'null': 'True', 'db_table': "'Event_Event'", 'to': u"orm['app.Event']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '15', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'events'", 'to': u"orm['app.Tag']", 'db_table': "'Event_Tag'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'app.person': {
            'Meta': {'object_name': 'Person', 'db_table': "'Person'"},
            'birth_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'birth_place': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'death_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'death_place': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['app.Event']", 'null': 'True', 'db_table': "'Event_Person'", 'blank': 'True'}),
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