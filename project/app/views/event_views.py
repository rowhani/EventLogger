#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import jdatetime
import uuid
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
        self.fields["photo"].widget = FileInput(attrs={"accept":"image/*"})
        self.fields["tags"].help_text = "دسته هایی را که این رویداد شامل آنها می شود انتخاب کنید"
        self.fields["related_events"].help_text = "رویدادهایی که قبلا اتفاق افتاده و مرتبط با این موضوع است، مانند دستگیری دوباره یک شخص و ...."
        self.fields["date_happened"].widget = DateInput(format="%d/%m/%Y")
        self.fields["date_ended"].widget = DateInput(format="%d/%m/%Y")
        
    def clean(self):
        cleaned_data = super(EventForm, self).clean()        
        validate_jalali_date(self, cleaned_data, "date_happened", True)
        validate_jalali_date(self, cleaned_data, "date_ended")   
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
        self.fields["birth_date"].widget = DateInput(format="%d/%m/%Y")
        self.fields["death_date"].widget = DateInput(format="%d/%m/%Y")
        
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
def modify_event_view(request, event_id=None, *args, **kwargs):
    active_link_id = "event"
    
    hash = 'event-tab'     
    existing_persons = 0
    person_type = 'select' 
    
    if event_id:
        action = reverse('edit_event', args=[event_id])
        event_instance = get_object_or_404(Event, pk=int(event_id))
        event_instance.date_happened = event_instance.jalali_date_happened
        event_instance.date_ended = event_instance.jalali_date_ended
        person_instance = event_instance.person
        if person_instance:
            person_instance.birth_date = person_instance.jalali_birth_date
            person_instance.death_date = person_instance.jalali_death_date
            existing_persons = person_instance.id
            person_type = 'create'
            person_create_title = 'اطلاعات شخصی را ویرایش کنید'
    else:
        action = reverse('add_event')
        event_instance = None
        person_instance = None
        
    if request.method == 'POST': 
        person_type = request.POST["person_type"]
        event_form = EventForm(request.POST, request.FILES, instance=event_instance)
        person_form = PersonForm(request.POST, request.FILES, instance=person_instance)
        existing_persons = int(request.POST.get('existing_persons', existing_persons))
        
        error = False
        if not event_form.is_valid():
            error = True
            hash = 'event-tab'
        elif person_type == 'create' and not person_form.is_valid():
            error = True
            hash = 'person-tab'
        if 'photo' in request.FILES and not request.FILES['photo'].content_type.startswith('image'):
            error = True
            hash = 'event-tab'
            event_form._errors['photo'] = ['تصویر معتبر نیست.']
        if 'person_photo' in request.FILES and not request.FILES['person_photo'].content_type.startswith('image'):
            error = True
            hash = 'person-tab'
            person_form._errors['person_photo'] = ['تصویر معتبر نیست.']
                        
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
            for et in EventTags.objects.filter(event=event):
                et.delete()
            for t in request.POST.getlist('tags'):      
                tag = Tag.objects.get(id=int(t))
                EventTags.objects.create(event=event, tag=tag)
                
            # Save related events
            if event_instance:
                for r in event.related_events.all():
                    event.related_events.remove(r)
            for r in request.POST.getlist('related_events'):      
                related_event = Event.objects.get(id=int(r))
                if related_event == event: continue
                event.related_events.add(related_event)
                event.save()
                
            # Save attachments
            for attachment in request.POST.getlist('remove_attachments'):
                attachment = Attachment.objects.get(id=int(attachment))
                try: os.remove("%s/%s" % (settings.EVENT_ATTACHMENTS_DIR , attachment.filename))
                except: pass
                attachment.delete()
            for attachment in request.FILES.getlist('attachments'):
                filename = save_request_file(settings.EVENT_ATTACHMENTS_DIR, attachment)
                Attachment.objects.create(name=attachment.name, filename=filename, event=event)
            
            # Save person
            person = None
            if person_type == 'create':
                person = person_form.save()
          
                if 'person_photo' in request.FILES:
                    try: os.remove("%s/%s" % (settings.PERSON_IMAGES_DIR , request.POST['person_photo_path']))
                    except: pass
                    person.person_photo = save_request_file(settings.PERSON_IMAGES_DIR, request.FILES['person_photo'])
                elif person_instance:
                    if 'remove_person_photo' not in request.POST:
                        person.person_photo = request.POST.get('person_photo_path', None)
                    else:
                        try: os.remove("%s/%s" % (settings.PERSON_IMAGES_DIR , person.person_photo))
                        except: pass
                        person.person_photo = None
                person.save()
            elif existing_persons:
                person = Person.objects.get(id=existing_persons)
            event.person = person             
            event.save()
            
            #return redirect("/event")
            return redirect("/event/edit/%s" % event.id)
    else:
        event_form = EventForm(instance=event_instance)
        person_form = PersonForm(instance=person_instance)
        
    title = 'ایجاد رویداد' if not event_id else 'ویرایش رویداد'    
    person_create_title = 'اطلاعات یک شخص جدید را وارد نمایید'    
    all_persons = [(p.id, unicode(p)) for p in Person.objects.all()]
    event_photo = event_instance and event_instance.photo or ''
    person_photo = person_instance and person_instance.person_photo or ''
    attachments = event_instance.attachments.all() if event_instance else []
    if event_instance: event_form.fields['related_events'].choices = filter(lambda r: r[0] != event_instance.id, event_form.fields['related_events'].choices)
      
    return render_to_response('event/add.html', locals(), context_instance = RequestContext(request))