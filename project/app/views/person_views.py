﻿#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import os
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.conf import settings
from django.forms import *
from django.forms.models import construct_instance

from app.models import *
from app.utils import *

######## Forms ########

class PersonForm(ModelForm):
    class Meta:
        model = Person   
        fields = ('first_name', 'last_name', 'gender', 'birth_date', 'birth_place', 'death_date', 'death_place', 'person_photo', 'events')
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'gender': 'جنسیت',
            'birth_date': 'تاریخ تولد',
            'birth_place': 'مکان تولد',
            'death_date': 'تاریخ صعود',
            'death_place': 'مکان صعود',
            'person_photo': 'تصویر شخص',
            'events': 'رویداد های مرتبط',
        }  
        
    def __init__(self, *args, **kwargs):
        super(PersonForm, self ).__init__(*args, **kwargs)
        self.fields["person_photo"].widget = FileInput(attrs={"accept":"image/*"})
        self.fields["gender"].choices = self.fields["gender"].choices[1:]
        self.fields["birth_date"].widget.attrs = {'data-role': 'calendar'}
        self.fields["birth_date"].widget.format = '%Y/%m/%d'
        self.fields["death_date"].widget.attrs = {'data-role': 'calendar'}
        self.fields["death_date"].widget.format = '%Y/%m/%d'
        self.fields["events"].help_text = "رویداد های که این شخص مرتبط به آن ها است."
        self.fields["events"].choices = Event.objects.filter(status="public").values_list('id', 'subject')
        self.fields["events"].widget.attrs = {'data-role': 'chosen'}
        
    def clean(self):
        cleaned_data = super(PersonForm, self).clean()        
        validate_jalali_date(self, cleaned_data, "birth_date")
        validate_jalali_date(self, cleaned_data, "death_date")   
        validate_image(self, cleaned_data, "person_photo")        
        return cleaned_data
 
######## Views ########

def list_person_view(request, *args, **kwargs):
    active_link_id = "person"
    
    return render_to_response('person/list.html', locals(), context_instance = RequestContext(request))
    
class PersonListJson(BaseDatatableView):
    model = Person
    columns = ['person_photo', 'first_name', 'birth_date', 'birth_place', 'events']
    order_columns = ['', 'first_name', 'birth_date', 'birth_place', 'events']
    max_display_length = 50
    
    def get_columns(self):
        if self.request.user.is_authenticated():
            self.columns.append('modified_by')
            self.order_columns.append('modified_by')
        return self.columns

    def render_column(self, row, column):  
        if column == 'first_name':
            return '<a href="%s">%s</a> <span class="%s"></span>' % (reverse('detail_person', args=[row.id]), "%s %s" % (row.first_name, row.last_name), "person-ended" if row.death_date else '')
        elif column == 'birth_date':
            return '<span class="convert-date">%s</span>' % row.birth_date.isoformat() if row.birth_date else ""
        elif column == 'death_date':
            return '<span class="convert-date">%s</span>' % row.death_date.isoformat() if row.death_date else ""
        elif column == 'modified_by':
            return row.modified_by.username if row.modified_by else 'Anonymous'
        elif column == 'person_photo':
            resp = """
                <a href="%(detail_url)s">
                    <span class="thumbnail">                           
                        %(person_photo)s
                    </span>
                </a>
                """ % {
                    "detail_url": reverse('detail_person', args=[row.id]),
                    "person_photo": ('<img src="%s%s"/>' % (settings.PERSON_IMAGES_URL, row.person_photo)).encode('utf-8', 'ignore') if row.person_photo else ('<span class="fa fa-male fa-3x"></span>' if row.gender == 'male' else '<span class="fa fa-female fa-3x"></span>' )
                }
            if self.request.user.is_authenticated():  
                resp += """
                    <div class="text-center">
                        <a class="btn btn-success btn-xs" title="ویرایش" href="%(edit_url)s">
                            <span class="glyphicon glyphicon-edit"></span>
                        </a>
                        <a class="btn btn-danger btn-xs" title="حذف" href="%(delete_url)s" data-confirm="آبا وافعا مایل به حذف شخص %(name)s هستید؟">
                            <span class="glyphicon glyphicon-trash"></span>
                        </a>
                    """ % {
                        "edit_url": reverse('edit_person', args=[row.id]),
                        "delete_url": reverse('delete_person', args=[row.id]),
                        "name": unicode(row).encode('utf-8', 'ignore')                    
                    }
                if row.status == 'public':
                    resp += """
                        <a class="btn btn-warning btn-xs" title="مخفی سازی" href="%s">
                            <span class="glyphicon glyphicon-eye-close"></span>
                        </a>
                    """ % reverse('change_status_person', args=[row.id, 'hidden'])
                elif row.status == 'hidden':
                    resp += """
                        <a class="btn btn-warning btn-xs" title="آشکار سازی" href="%s">
                            <span class="glyphicon glyphicon-eye-open"></span>
                        </a>
                    """ % reverse('change_status_person', args=[row.id, 'public'])
                elif row.status == 'unconfirmed':
                    resp += """
                        <a class="btn btn-warning btn-xs" title="تایید" href="%s">
                            <span class="glyphicon glyphicon-ok"></span>
                        </a>
                    """ % reverse('change_status_person', args=[row.id, 'public'])
                resp += "</div>"
            return resp
        elif column == 'events':
            return "<br/> ".join(['<a href="%s">%s</a>' % (reverse('detail_event', args=[event.id]), unicode(event)) for event in row.events.filter(status='public')])
        else:
            return super(PersonListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        status_filter = self.request.GET.getlist('status_filter[]', [])
        if sSearch:
            qs = qs.filter(Q(first_name__icontains=sSearch)|Q(last_name__icontains=sSearch))
        if self.request.user.is_authenticated():
            if status_filter:
                qs = qs.filter(status__in=status_filter)
        else:
            qs = qs.filter(status='public')
        return qs
        
    def get_initial_queryset(self):
        return super(PersonListJson, self ).get_initial_queryset()
        
    def prepare_results(self, qs):
        return super(PersonListJson, self ).prepare_results(qs)

def detail_person_view(request, person_id, *args, **kwargs):
    active_link_id = "person"
    
    person = get_object_or_404(Person, pk=int(person_id))
    return render_to_response('person/detail.html', locals(), context_instance = RequestContext(request))
    
@login_required
def delete_person_view(request, person_id, *args, **kwargs):
    person = get_object_or_404(Person, pk=int(person_id))
    person.delete()
    return redirect(reverse('list_person'))
    
@login_required 
def change_status_person_view(request, person_id, status, *args, **kwargs):
    person = get_object_or_404(Person, pk=int(person_id))
    person.status = status
    person.save()
    if request.GET.get('show_detail', None) == '1':
        return redirect(reverse('detail_person', args=[person.id]))
    else:
        return redirect(reverse('list_person'))
   
@login_required
def modify_person_view(request, person_id=None, *args, **kwargs):
    active_link_id = "person"    
    
    if person_id:
        action = reverse('edit_person', args=[person_id])
        person_instance = get_object_or_404(Person, pk=int(person_id))
        title = "ویرایش شخص"
    else:
        action = reverse('add_person')
        person_instance = None
        title = "ایجاد شخص"
        
    if request.method == 'POST': 
        person_form = PersonForm(request.POST, request.FILES, instance=person_instance, auto_id='%s')
        if person_form.is_valid():
            person = person_form.save()
            
            if 'person_photo' in request.FILES:
                try: os.remove("%s/%s" % (settings.PERSON_IMAGES_DIR , request.POST['person_photo_path']))
                except: pass
                person.person_photo = save_request_file(settings.PERSON_IMAGES_DIR, request.FILES['person_photo'])
            elif person_instance:
                if 'remove_photo' not in request.POST:
                    person.person_photo = request.POST.get('person_photo_path', None)
                else:
                    try: os.remove("%s/%s" % (settings.PERSON_IMAGES_DIR , person.person_photo))
                    except: pass
                    person.person_photo = None
            if request.user.is_authenticated(): person.modified_by = request.user
            person.save()
            
            # Save persons
            if person_instance:
                for i in person.events.all():
                    person.events.remove(i)
            for i in request.POST.getlist('events'):      
                event = Event.objects.get(id=int(i))
                person.events.add(event) 
                
            return redirect(reverse('detail_person', args=[person.id]))
        else:
            person_form.fields['birth_place'].widget.attrs.update({'data-ignore-convert':'1'})
            person_form.fields['death_date'].widget.attrs.update({'data-ignore-convert':'1'})
    else:
        person_form = PersonForm(instance=person_instance, auto_id='%s')                            
        
    person_photo = person_instance and person_instance.person_photo or ''
        
    return render_to_response('person/modify.html', locals(), context_instance = RequestContext(request))
    