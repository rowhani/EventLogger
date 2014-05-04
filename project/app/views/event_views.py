#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
import jdatetime
from django.forms import *
from app.models import *

@login_required
def list_event_view(request, *args, **kwargs):
    active_link_id = "event"
    return render_to_response('event/list.html', locals(), context_instance = RequestContext(request))

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ('subject', 'date_happened', 'date_ended', 'description', 'actions_taken', 'tags', 'related_events', 'photo')
        labels = {
            'subject': 'موضوع',
            'date_happened': 'تاریخ وقوع',
            'date_ended': 'تاریخ اتمام',
            'description': 'شرح رویداد',
            'actions_taken': 'عملیات انجام شده برای رفع رویداد',
            'tags': 'دسته ها',
            'related_events': 'رویدادهای مرتبط',
            'photo': 'تصویر'
        }
        widgets = {
            'tags': TextInput(attrs={'data-role': 'sourcetagsinput'}),
            'related_events': SelectMultiple(attrs={'cols': 80, 'rows': 20}),
        }
        
class LocationForm(ModelForm):
    class Meta:
        model = Location       

class PersonForm(ModelForm):
    class Meta:
        model = Person   

class AttachmentForm(ModelForm):
    class Meta:
        model = Attachment         
        
@login_required
def add_event_view(request, *args, **kwargs):
    ##print "********", request.POST
    ##print "***", jdatetime.datetime.strptime(request.POST['date_happened'], '%d/%m/%Y').togregorian() 
    active_link_id = "event"
    all_tags = json.dumps([t.name for t in Tag.objects.all()]).encode("utf-8")
    if request.method == 'POST': 
        event_form = EventForm(request.POST)
        location_form = LocationForm(request.POST)
        person_form = PersonForm(request.POST)
        attachment_form = AttachmentForm(request.POST)
    else:
        event_form = EventForm()
        location_form = LocationForm()
        person_form = PersonForm()
        attachment_form = AttachmentForm()
    return render_to_response('event/add.html', locals(), context_instance = RequestContext(request))