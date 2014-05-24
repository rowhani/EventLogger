# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table('Event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('description_raw', self.gf('django.db.models.fields.TextField')(db_index=True, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=1000, db_index=True)),
            ('date_happened', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_ended', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('actions_taken', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='public', max_length=15, blank=True)),
        ))
        db.send_create_signal(u'app', ['Event'])

        # Adding M2M table for field persons on 'Event'
        m2m_table_name = 'Event_Person'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'app.event'], null=False)),
            ('person', models.ForeignKey(orm[u'app.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['event_id', 'person_id'])

        # Adding M2M table for field tags on 'Event'
        m2m_table_name = 'Event_Tag'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'app.event'], null=False)),
            ('tag', models.ForeignKey(orm[u'app.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['event_id', 'tag_id'])

        # Adding M2M table for field related_events on 'Event'
        m2m_table_name = 'Event_Event'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_event', models.ForeignKey(orm[u'app.event'], null=False)),
            ('to_event', models.ForeignKey(orm[u'app.event'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_event_id', 'to_event_id'])

        # Adding model 'Person'
        db.create_table('Person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('birth_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('birth_place', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('death_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('death_place', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('person_photo', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='public', max_length=15, blank=True)),
        ))
        db.send_create_signal(u'app', ['Person'])

        # Adding model 'Tag'
        db.create_table('Tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'app', ['Tag'])

        # Adding model 'Attachment'
        db.create_table('Attachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('filename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1000)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['app.Event'])),
        ))
        db.send_create_signal(u'app', ['Attachment'])


    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table('Event')

        # Removing M2M table for field persons on 'Event'
        db.delete_table('Event_Person')

        # Removing M2M table for field tags on 'Event'
        db.delete_table('Event_Tag')

        # Removing M2M table for field related_events on 'Event'
        db.delete_table('Event_Event')

        # Deleting model 'Person'
        db.delete_table('Person')

        # Removing M2M table for field events on 'Person'
        db.delete_table('Event_Person')

        # Deleting model 'Tag'
        db.delete_table('Tag')

        # Deleting model 'Attachment'
        db.delete_table('Attachment')


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
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
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