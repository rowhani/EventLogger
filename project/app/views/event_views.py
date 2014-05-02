#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.forms import *
from app.models import *

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ('subject', 'location', 'date_happened', 'date_ended', 'description', 'actions_taken', 'tags', 'related_events')
        labels = {
            'subject': 'موضوع',
            'location': 'مکان',
            'date_happened': 'تاریخ وقوع',
            'date_ended': 'تاریخ اتمام',
            'description': 'شرح رویداد',
            'actions_taken': 'عملیات انجام شده برای رفع رویداد',
            'tags': 'دسته ها',
            'related_events': 'رویدادهای مرتبط',
        }
        widgets = {
            'tags': TextInput(attrs={'data-role': 'sourcetagsinput'}),
            'related_events': SelectMultiple(attrs={'cols': 80, 'rows': 20}),
        }
        
@login_required
def add_event_view(request, *args, **kwargs):
    all_tags = json.dumps([t.name for t in Tag.objects.all()]).encode("utf-8")
    if request.method == 'POST': 
        form = EventForm(request.POST)
    else:
        form = EventForm()
    return render_to_response('event/add.html', locals(), context_instance = RequestContext(request))