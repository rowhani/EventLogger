#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import jdatetime
import uuid
import os
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.forms import *
from django.forms.models import construct_instance

from app.models import *

######## Forms ########

def validate_jalali_date(form, cleaned_data, field, check_required=False):
    dt = form.data.get(field, None)
    if field in form._errors: del form._errors[field]
    if not dt:
        if check_required:
            form._errors[field] = "این فیلد لازم است."
    else:
        try: cleaned_data[field] = jdatetime.datetime.strptime(dt, '%d/%m/%Y').togregorian()
        except: form._errors[field] = "یک تاریخ/زمان معتبر وارد کنید."
        
def save_request_file(destination, request_file):
    ext = os.path.splitext(request_file.name)[1]
    name =  "%s%s" % (uuid.uuid4(), ext)
    path = "%s/%s" % (destination, name)
    with open(path, 'wb+') as f:
        for chunk in request_file.chunks(): f.write(chunk) 
    print "###PHOTO", name
    return name

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
            'photo': 'تصویر',
            'tags': 'دسته ها',
            'related_events': 'رویدادهای مرتبط'
        }
        help_texts = {
            'date_ended': 'تاریخی که در آن مشکل مرتفع شده یا به نحوی پایان پذیرفته است.',
            'location': 'برای جستجوی بهتر می توانید آدرس کامل را همراه با نام استان و شهر ذکر کنید.',            
            'actions_taken': 'اقداماتی که ممکن است برای رفع رویداد یا به جهت تظلم خواهی انجام شده باشد.'
        }
        
    def __init__(self, *args, **kwargs):
        super(EventForm, self ).__init__(*args, **kwargs)
        self.fields["photo"].widget = FileInput(attrs={})
        self.fields["tags"].help_text = "دسته هایی را که این رویداد شامل آنها می شود انتخاب با ایجاد کنید (با نوشتن نام دسته و فشار دادن کلید Enter)"
        self.fields["related_events"].help_text = "رویدادهایی که قبلا اتفاق افتاده و مرتبط با این موضوع است، مانند دستگیری دوباره یک شخص و ...."
        
    def clean(self):
        cleaned_data = super(EventForm, self).clean()        
        validate_jalali_date(self, cleaned_data, "date_happened", True)
        validate_jalali_date(self, cleaned_data, "date_ended")            
        return cleaned_data
        
    def save_m2m(self):
        pass

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
        self.fields["person_photo"].widget = FileInput(attrs={})
        self.fields["gender"].choices = self.fields["gender"].choices[1:]
        
    def clean(self):
        cleaned_data = super(PersonForm, self).clean()        
        validate_jalali_date(self, cleaned_data, "birth_date")
        validate_jalali_date(self, cleaned_data, "death_date")            
        return cleaned_data

######## Views ########

@login_required
def list_event_view(request, *args, **kwargs):
    active_link_id = "event"
    return render_to_response('event/list.html', locals(), context_instance = RequestContext(request))
   
@login_required
def add_event_view(request, *args, **kwargs):
    active_link_id = "event"
    hash = 'event-tab'
    all_tags = json.dumps([t.name for t in Tag.objects.all()]).encode("utf-8")
    all_persons = [(p.id, unicode(p)) for p in Person.objects.all()]
        
    if request.method == 'POST': 
        print "*********", request.FILES.getlist('attachments')
        
        person_type = request.POST["person_type"]
        event_form = EventForm(request.POST, request.FILES)
        person_form = PersonForm(request.POST, request.FILES) if person_type == 'create' else PersonForm() 
        existing_persons = int(request.POST.get('existing_persons', 0))
        error = False
        if not event_form.is_valid():
            error = True
            hash = 'event-tab'
        elif person_type == 'create' and not person_form.is_valid():
            error = True
            hash = 'person-tab'
        if not error:
            # Save event
            event = construct_instance(event_form, event_form.instance, ['subject', 'date_happened', 'date_ended', 'location', 'description', 'actions_taken'])
            if 'photo' in request.FILES:
                event.photo = save_request_file(settings.EVENT_IMAGES_DIR, request.FILES['photo'])
                
            #TODO save tags and related events and attachments
            
            #Save person
            person = None
            if person_type == 'create':
                person = person_form.save()
                if 'person_photo' in request.FILES:
                    person.person_photo = save_request_file(settings.PERSON_IMAGES_DIR, request.FILES['person_photo'])
                    person.save()
            elif existing_persons:
                person = Person.objects.get(id=existing_persons)
            event.person = person 
            
            event.save()
            
            return redirect("/event")
    else:
        person_type = 'select'
        event_form = EventForm()
        person_form = PersonForm()
        
    for event in Event.objects.all():
        print "***", event.photo
    
    return render_to_response('event/add.html', locals(), context_instance = RequestContext(request))