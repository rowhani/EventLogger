﻿#! /usr/bin/env python2.7

import jdatetime
import re
import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from utils import *

class TrimCharField(models.CharField):
   def get_prep_value(self, value):
       try: return super(TrimCharField, self).get_prep_value(value).strip()
       except: return super(TrimCharField, self).get_prep_value(value)

   def pre_save(self, model_instance, add):
       try: return super(TrimCharField, self).pre_save(model_instance, add).strip()
       except: return super(TrimCharField, self).pre_save(model_instance, add)
       
class Event(models.Model):
    class Meta: 
        db_table = "Event"
        ordering = ['-date_happened', 'subject']
        
    subject = TrimCharField(max_length=200, db_index=True)
    description = models.TextField()
    description_raw = models.TextField(db_index=True, null=True, blank=True)
    location = TrimCharField(max_length=1000, db_index=True)
    date_happened = models.DateTimeField()
    date_ended = models.DateTimeField(null=True, blank=True)
    photo = TrimCharField(max_length=1000, null=True, blank=True)
    actions_taken = models.TextField(null=True, blank=True)
    persons = models.ManyToManyField("Person", null=True, blank=True, db_table="Event_Person")
    tags = models.ManyToManyField('Tag', null=True, blank=True, related_name="events", db_table="Event_Tag")
    related_events = models.ManyToManyField("self", null=True, blank=True, db_table="Event_Event")
    status = models.CharField(max_length=15, blank=True, default='public', choices=[('public', 'public'), ('unconfirmed', 'unconfirmed'), ('hidden', 'hidden')])
    modified_by = models.ForeignKey(User, null=True, blank=True)
        
    def __unicode__(self):
        return "%s (%s)" % (self.subject, self.location)
        
    def save(self, *args, **kwargs):
        self.description_raw = re.sub(r'(<!--.*?-->|<[^>]*>)', '', self.description).replace("&nbsp;", " ")
        super(Event, self).save(*args, **kwargs)
        
    def delete(self):
        try: os.remove("%s/%s" % (settings.EVENT_IMAGES_DIR , self.photo))
        except: pass
        for attachment in self.attachments.all():
            attachment.delete()
        super(Event, self).delete()
        
    @property
    def jalali_date_happened(self):
        try: return jdatetime.date.fromgregorian(date=self.date_happened.date())
        except: return self.date_happened
        
    @property
    def jalali_date_ended(self):
        try: return jdatetime.date.fromgregorian(date=self.date_ended.date())
        except: return self.date_ended
        
    @property
    def truncated_description(self):
        return get_truncated_text(self.description_raw, boundry_letters_count=150)
 
class Person(models.Model):
    class Meta: 
        db_table = "Person"
        ordering = ['first_name', 'last_name']
        
    first_name = TrimCharField(max_length=200, db_index=True)
    last_name = TrimCharField(max_length=200, db_index=True)
    gender = models.CharField(max_length=10, blank=False, choices=[('male', 'مرد'), ('female', 'زن')])
    birth_date = models.DateTimeField(null=True, blank=True)
    birth_place = TrimCharField(max_length=1000, null=True, blank=True)
    death_date = models.DateTimeField(null=True, blank=True)
    death_place = TrimCharField(max_length=1000, null=True, blank=True)
    person_photo = TrimCharField(max_length=1000, null=True, blank=True)
    events = models.ManyToManyField("Event", null=True, blank=True, db_table="Event_Person")
    status = models.CharField(max_length=15, blank=True, default='public', choices=[('public', 'public'), ('unconfirmed', 'unconfirmed'), ('hidden', 'hidden')])
    modified_by = models.ForeignKey(User, null=True, blank=True)
        
    def __unicode__(self):
        if self.birth_place:
            return "%s %s (%s)" % (self.first_name, self.last_name, self.birth_place)
        else: 
            return "%s %s" % (self.first_name, self.last_name)
            
    def delete(self):
        try: os.remove("%s/%s" % (settings.PERSON_IMAGES_DIR , self.person_photo))
        except: pass
        super(Person, self).delete()
            
    @property
    def jalali_birth_date(self):
        try: return jdatetime.date.fromgregorian(date=self.birth_date.date())
        except: return self.birth_date
        
    @property
    def jalali_death_date(self):
        try: return jdatetime.date.fromgregorian(date=self.death_date.date())
        except: return self.death_date
                
class Tag(models.Model):
    class Meta: 
        db_table = "Tag"
        ordering = ['name']
        
    name = TrimCharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name
    
class Attachment(models.Model):
    class Meta: 
        db_table = "Attachment"     
        ordering = ['name']
        
    name = TrimCharField(max_length=255)
    filename = TrimCharField(max_length=1000, unique=True)
    event = models.ForeignKey("Event", related_name="attachments")
    
    def __unicode__(self):
        return self.name
        
    def delete(self):
        try: os.remove("%s/%s" % (settings.EVENT_ATTACHMENTS_DIR , self.filename))
        except: pass
        super(Attachment, self).delete()