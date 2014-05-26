#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import os
from captcha.fields import CaptchaField
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.conf import settings
from django.forms import *
from django.forms.models import construct_instance

from app.models import *
from app.utils import *

######## Forms ########

class EventForm(ModelForm):
    attachments = FileField(label='ضمائم', widget=FileInput(attrs={'multiple': 'multiple'}), help_text='می توانید چندین فایل را ضمیمه کنید.', required=False)
    captcha = CaptchaField(label='کد امنیتی', error_messages={'invalid': 'کد امنیتی اشتیاه وارد شده است.'})
    
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
        self.fields["photo"].help_text = "تصویر انتخاب شده جایگزین تصویر قبلی خواهد شد."
        self.fields["tags"].help_text = "دسته هایی را که این رویداد شامل آنها می شود انتخاب کنید."
        self.fields["tags"].widget.attrs = {'data-role': 'chosen'}
        self.fields["related_events"].help_text = "رویدادهایی که قبلا اتفاق افتاده و مرتبط با این موضوع است، مانند دستگیری دوباره یک شخص و ...."
        self.fields["related_events"].choices = Event.objects.filter(status="public").exclude(id=self.instance.id if self.instance else 0).values_list('id', 'subject')
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
        fields = ('first_name', 'last_name', 'gender', 'birth_date', 'birth_place', 'death_date', 'death_place', 'person_photo')
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
        self.fields["persons"].choices = [(p.id, unicode(p)) for p in Person.objects.filter(status="public")]

######## Views ########

def list_event_view(request, *args, **kwargs):
    active_link_id = "event"
    
    return render_to_response('event/list.html', locals(), context_instance = RequestContext(request))
    
class EventListJson(BaseDatatableView):
    model = Event
    columns = ['photo', 'subject', 'date_happened', 'location', 'persons']
    order_columns = ['', 'subject', 'date_happened', 'location', '']
    max_display_length = 50

    def render_column(self, row, column):  
        if column == 'subject':
            return '<a href="%s">%s</a> <span class="%s"></span>' % (reverse('detail_event', args=[row.id]), row.subject, "event-ended" if row.date_ended else '')
        elif column == 'date_happened':
            return '<span class="convert-date">%s</span>' % row.date_happened
        elif column == 'photo':
            resp = """
                <a href="%(detail_url)s">
                    <span class="thumbnail">                           
                        %(photo)s
                    </span>
                </a>
                """ % {
                    "detail_url": reverse('detail_event', args=[row.id]),
                    "photo": ('<img src="%s%s"/>' % (settings.EVENT_IMAGES_URL, row.photo)).encode('utf-8', 'ignore') if row.photo else '<span class="fa fa-picture-o fa-3x"></span>'
                }
            if self.request.user.is_authenticated():  
                resp += """
                    <div class="text-center">
                        <a class="btn btn-success btn-xs" title="ویرایش" href="%(edit_url)s">
                            <span class="glyphicon glyphicon-edit"></span>
                        </a>
                        <a class="btn btn-danger btn-xs" title="حذف" href="%(delete_url)s" data-confirm="آبا وافعا مایل به حذف رویداد %(subject)s هستید؟">
                            <span class="glyphicon glyphicon-trash"></span>
                        </a>
                    """ % {
                        "edit_url": reverse('edit_event', args=[row.id]),
                        "delete_url": reverse('delete_event', args=[row.id]),
                        "subject": row.subject.encode('utf-8', 'ignore')                    
                    }
                if row.status == 'public':
                    resp += """
                        <a class="btn btn-warning btn-xs" title="مخفی سازی" href="%s">
                            <span class="glyphicon glyphicon-eye-close"></span>
                        </a>
                    """ % reverse('change_status_event', args=[row.id, 'hidden'])
                elif row.status == 'hidden':
                    resp += """
                        <a class="btn btn-warning btn-xs" title="آشکار سازی" href="%s">
                            <span class="glyphicon glyphicon-eye-open"></span>
                        </a>
                    """ % reverse('change_status_event', args=[row.id, 'public'])
                elif row.status == 'unconfirmed':
                    resp += """
                        <a class="btn btn-warning btn-xs" title="تایید" href="%s">
                            <span class="glyphicon glyphicon-ok"></span>
                        </a>
                    """ % reverse('change_status_event', args=[row.id, 'public'])
                resp += "</div>"
            return resp
        elif column == 'persons':
            return "<br/> ".join(['<a href="%s">%s</a>' % (reverse('detail_person', args=[person.id]), unicode(person)) for person in row.persons.filter(status='public')])
        else:
            return super(EventListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        status_filter = self.request.GET.getlist('status_filter[]', [])
        if sSearch:
            qs = qs.filter(subject__icontains=sSearch)
        if self.request.user.is_authenticated():
            if status_filter:
                qs = qs.filter(status__in=status_filter)
        else:
            qs = qs.filter(status='public')
        return qs
        
    def get_initial_queryset(self):
        return super(EventListJson, self ).get_initial_queryset()
        
    def prepare_results(self, qs):
        return super(EventListJson, self ).prepare_results(qs)

def detail_event_view(request, event_id, *args, **kwargs):
    active_link_id = "event"
    
    event = get_object_or_404(Event, pk=int(event_id))
    return render_to_response('event/detail.html', locals(), context_instance = RequestContext(request))
    
@login_required
def delete_event_view(request, event_id, *args, **kwargs):
    event = get_object_or_404(Event, pk=int(event_id))
    event.delete()
    return redirect(reverse('list_event'))
    
@login_required 
def change_status_event_view(request, event_id, status, *args, **kwargs):
    event = get_object_or_404(Event, pk=int(event_id))
    event.status = status
    event.save()
    if status == 'public':
        for person in event.persons.all():
            person.status = 'public'
            person.save()
    if request.GET.get('show_detail', None) == '1':
        return redirect(reverse('detail_event', args=[event.id]))
    else:
        return redirect(reverse('list_event'))
   
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
        if request.user.is_authenticated(): del event_form.fields['captcha']
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
            if not request.user.is_authenticated(): event.status = 'unconfirmed'
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
                if not request.user.is_authenticated(): person.status = 'unconfirmed'
                person_photo = '%s-person_photo' % person_form.prefix
                if person_photo in request.FILES:
                    person.person_photo = save_request_file(settings.PERSON_IMAGES_DIR, request.FILES[person_photo])
                    person.save()
                event.persons.add(person)
          
            return redirect(reverse('detail_event', args=[event.id]))
        else:
            event_form.fields['date_happened'].widget.attrs.update({'data-ignore-convert':'1'})
            event_form.fields['date_ended'].widget.attrs.update({'data-ignore-convert':'1'})
            for person_form in person_forms:
                person_form.fields['birth_date'].widget.attrs.update({'data-ignore-convert':'1'})
                person_form.fields['death_date'].widget.attrs.update({'data-ignore-convert':'1'})
    else:
        event_form = EventForm(instance=event_instance, auto_id='%s')
        if request.user.is_authenticated(): del event_form.fields['captcha']
        existing_persons_form = ExistingPersonsForm(instance=event_instance, auto_id='%s')
        person_forms = []
        
    title = 'ارسال رویداد جدید' if not request.user.is_authenticated() else ('ایجاد رویداد جدید' if not event_id else 'ویرایش رویداد')
    event_photo = event_instance and event_instance.photo or ''
    attachments = event_instance.attachments.all() if event_instance else []
      
    return render_to_response('event/modify.html', locals(), context_instance = RequestContext(request))
    