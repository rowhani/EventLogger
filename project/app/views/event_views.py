﻿#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import os
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from django.forms import *
from django.forms.models import construct_instance

from app.models import *
from app.utils import *

######## Forms ########

class EventForm(ModelForm):
    attachments = FileField(label='ضمائم', widget=FileInput(attrs={'multiple': 'multiple'}), help_text='می توانید چندین فایل را ضمیمه کنید', required=False)
    
    class Meta:
        model = Event
        fields = ('subject', 'date_happened', 'date_ended', 'location', 'description', 'actions_taken', 'tags', 'related_events', 'photo')
        labels = {
            'subject': 'موضوع',
            'date_happened': 'تاریخ وقوع',
            'date_ended': 'تاریخ اتمام',
            'location': 'مکان وقوع',
            'description': 'شرح رویداد',
            'actions_taken': 'اقدامات انجام شده',
            'tags': 'دسته ها',
            'related_events': 'رویدادهای مرتبط',
            'photo': 'تصویر',
        }
        help_texts = {
            'date_ended': 'تاریخی که در آن مشکل مرتفع شده یا به نحوی پایان پذیرفته است.',
            'location': 'برای جستجوی بهتر می توانید آدرس کامل را همراه با نام استان و شهر ذکر کنید.',            
            'actions_taken': 'اقداماتی که ممکن است برای رفع رویداد یا به جهت تظلم خواهی انجام شده باشد.'
        }
        
    def __init__(self, *args, **kwargs):
        super(EventForm, self ).__init__(*args, **kwargs)
        self.fields["photo"].widget = FileInput(attrs={"accept":"image/*"})
        self.fields["tags"].help_text = "دسته هایی را که این رویداد شامل آنها می شود انتخاب کنید"
        self.fields["tags"].widget.attrs = {'data-role': 'chosen'}
        self.fields["related_events"].help_text = "رویدادهایی که قبلا اتفاق افتاده و مرتبط با این موضوع است، مانند دستگیری دوباره یک شخص و ...."
        self.fields["related_events"].widget.attrs = {'data-role': 'chosen'}
        self.fields["date_happened"].widget.attrs = {'data-role': 'calendar'}
        self.fields["date_ended"].widget.attrs = {'data-role': 'calendar'}  
        self.fields["description"].widget.attrs = {'data-role': 'wysihtml5'}   
        self.fields["actions_taken"].widget.attrs = {'data-role': 'wysihtml5'}         
        
    def clean(self):
        cleaned_data = super(EventForm, self).clean()        
        validate_jalali_date(self, cleaned_data, "date_happened", True)
        validate_jalali_date(self, cleaned_data, "date_ended")   
        validate_image(self, cleaned_data, "photo")
        if 'tags' in self._errors: del self._errors['tags']
        return cleaned_data

class PersonForm(ModelForm):
    class Meta:
        model = Person   
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'gender': 'جنسیت',
            'birth_date': 'تاریخ تولد',
            'birth_place': 'مکان تولد',
            'death_date': 'تاریخ صعود',
            'death_place': 'مکان صعود',
            'person_photo': 'تصویر شخص',
        }  
        
    def __init__(self, *args, **kwargs):
        super(PersonForm, self ).__init__(*args, **kwargs)
        self.fields["person_photo"].widget = FileInput(attrs={"accept":"image/*"})
        self.fields["gender"].choices = self.fields["gender"].choices[1:]
        self.fields["birth_date"].widget.attrs = {'data-role': 'calendar'}
        self.fields["death_date"].widget.attrs = {'data-role': 'calendar'}
        
    def clean(self):
        cleaned_data = super(PersonForm, self).clean()        
        validate_jalali_date(self, cleaned_data, "birth_date")
        validate_jalali_date(self, cleaned_data, "death_date")   
        validate_image(self, cleaned_data, "person_photo")        
        return cleaned_data
        
class ExistingPersonsForm(ModelForm):
    new_persons = CharField(widget=HiddenInput())
    
    class Meta:
        model = Event
        fields = ('persons',)
        
    def __init__(self, *args, **kwargs):
        super(ExistingPersonsForm, self ).__init__(*args, **kwargs)
        self.fields["persons"].label = "لیست اشخاص موجود"
        self.fields["persons"].help_text = "می توانید از لیست اشخاص موجود در سیستم انتخاب کنید."
        self.fields["persons"].widget.attrs = {'data-role': 'chosen'}

######## Views ########

@login_required
def list_event_view(request, *args, **kwargs):
    active_link_id = "event"
    
    events = Event.objects.all()
    return render_to_response('event/list.html', locals(), context_instance = RequestContext(request))
    
@login_required
def detail_event_view(request, event_id, *args, **kwargs):
    active_link_id = "event"
    return render_to_response('event/detail.html', locals(), context_instance = RequestContext(request))
   
@login_required
def modify_event_view(request, event_id=None, *args, **kwargs):
    active_link_id = "event"
    
    hash = 'event-tab'   
    main_person_form = PersonForm(auto_id='%s', prefix="main")
    person_form_prefix = 'person_from'
    person_form_number = 1    
    
    if event_id:
        action = reverse('edit_event', args=[event_id])
        event_instance = get_object_or_404(Event, pk=int(event_id))
    else:
        action = reverse('add_event')
        event_instance = None
        
    if request.method == 'POST': 
        event_form = EventForm(request.POST, request.FILES, instance=event_instance, auto_id='%s')
        existing_persons_form = ExistingPersonsForm(request.POST, request.FILES, instance=event_instance, auto_id='%s')
        
        person_forms = []
        person_form_prefixes = filter(lambda p: p, request.POST['new_persons'].split(","))    
        existing_persons_form.fields['new_persons'].initial = ",".join(person_form_prefixes)
        for prefix in person_form_prefixes:
            person_forms.append(PersonForm(request.POST, request.FILES, auto_id='%s', prefix=prefix))
        person_form_number = max(map(lambda p: int(p.replace(person_form_prefix, "")), person_form_prefixes) or [0]) + 1
                
        error = False
        if not event_form.is_valid():
            error = True
            hash = 'event-tab'
        for person_form in person_forms:
            if not person_form.is_valid():
                error = True
                hash = 'person-tab'
                        
        if not error:
            # Save event
            event = construct_instance(event_form, event_form.instance, ['subject', 'date_happened', 'date_ended', 'location', 'description', 'actions_taken', 'related_events'])
            
            if 'photo' in request.FILES:
                try: os.remove("%s/%s" % (settings.EVENT_IMAGES_DIR , request.POST['photo_path']))
                except: pass
                event.photo = save_request_file(settings.EVENT_IMAGES_DIR, request.FILES['photo'])
            elif event_instance:
                if 'remove_photo' not in request.POST:
                    event.photo = request.POST.get('photo_path', None)
                else:
                    try: os.remove("%s/%s" % (settings.EVENT_IMAGES_DIR , event.photo))
                    except: pass
                    event.photo = None
            event.save()
                
            # Save tags
            if event_instance:
                for i in event.tags.all():
                    event.tags.remove(i)
            for i in request.POST.getlist('tags'):      
                tag = Tag.objects.get(id=int(i))
                event.tags.add(tag)
                
            # Save related events
            if event_instance:
                for i in event.related_events.all():
                    event.related_events.remove(i)
            for i in request.POST.getlist('related_events'):      
                related_event = Event.objects.get(id=int(i))
                if related_event != event:
                    event.related_events.add(related_event)
                
            # Save attachments
            for attachment in request.POST.getlist('remove_attachments'):
                attachment = Attachment.objects.get(id=int(attachment))
                try: os.remove("%s/%s" % (settings.EVENT_ATTACHMENTS_DIR , attachment.filename))
                except: pass
                attachment.delete()
            for attachment in request.FILES.getlist('attachments'):
                filename = save_request_file(settings.EVENT_ATTACHMENTS_DIR, attachment)
                Attachment.objects.create(name=attachment.name, filename=filename, event=event)
                
            # Save persons
            if event_instance:
                for i in event.persons.all():
                    event.persons.remove(i)
            for i in request.POST.getlist('persons'):      
                person = Person.objects.get(id=int(i))
                event.persons.add(person)
            for person_form in person_forms:
                person = person_form.save()
                person_photo = '%s-person_photo' % person_form.prefix
                if person_photo in request.FILES:
                    person.person_photo = save_request_file(settings.PERSON_IMAGES_DIR, request.FILES[person_photo])
                    person.save()
                event.persons.add(person)
          
            return redirect(reverse('edit_event', args=[event.id])) #redirect(reverse('detail_event', args=[event_id]))
        else:
            event_form.fields['date_happened'].widget.attrs.update({'data-ignore-convert':'1'})
            event_form.fields['date_ended'].widget.attrs.update({'data-ignore-convert':'1'})
            for person_form in person_forms:
                person_form.fields['birth_date'].widget.attrs.update({'data-ignore-convert':'1'})
                person_form.fields['death_date'].widget.attrs.update({'data-ignore-convert':'1'})
    else:
        event_form = EventForm(instance=event_instance, auto_id='%s')
        existing_persons_form = ExistingPersonsForm(instance=event_instance, auto_id='%s')
        person_forms = []
        
    title = 'ایجاد رویداد' if not event_id else 'ویرایش رویداد'    
    event_photo = event_instance and event_instance.photo or ''
    attachments = event_instance.attachments.all() if event_instance else []
    if event_instance: 
        event_form.fields['related_events'].choices = filter(lambda r: r[0] != event_instance.id, event_form.fields['related_events'].choices)
      
    return render_to_response('event/add.html', locals(), context_instance = RequestContext(request))
    