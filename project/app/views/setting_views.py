#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import os
import zipfile
import tablib
import shutil
from StringIO import StringIO
from datetime import datetime
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse
from django.conf import settings
from django.forms import *
from django.forms.models import construct_instance

from app.models import *
from app.resources import *

#Monkey Patch (put csv first)
from tablib import formats
formats.available = (formats.csv, formats.json, formats.xls, formats.yaml, formats.tsv, formats.html, formats.xlsx, formats.ods)

media_root_base = os.path.basename(settings.MEDIA_ROOT)

@login_required
def setting_view(request, *args, **kwargs):
    active_link_id = "setting"
    
    restore_error = request.GET.get('restore_error', '0') == '1'
    restore_success = request.GET.get('restore_success', '0') == '1'
        
    return render_to_response('setting.html', locals(), context_instance = RequestContext(request))
    
@login_required
def setting_backup(request, *args, **kwargs):   
    include_files = request.POST.get('include_files', False)
    
    events = EventResource().export().csv
    persons = PersonResource().export().csv
    tags = TagResource().export().csv
    attachments = AttachmentResource().export().csv
    
    buffer = StringIO()
    zf = zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED)
    
    zf.writestr('events.csv', events)
    zf.writestr('persons.csv', persons)
    zf.writestr('tags.csv', tags)
    zf.writestr('attachments.csv', attachments)
    
    if include_files:
        for dirname, subdirs, files in os.walk(settings.MEDIA_ROOT):
            for filename in files:
                source = os.path.join(dirname, filename)
                destination = os.path.join(media_root_base, os.path.basename(dirname), filename)
                zf.write(source, destination)
                
    zf.close()
    
    response = HttpResponse(content_type=' application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="Backup_%s.zip"' % datetime.now().strftime("%Y_%m_%d")
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response    
    
@login_required
def setting_restore(request, *args, **kwargs):       
    backup_file = request.FILES.get('backup_file', None)
    ignore_errors = request.POST.get('ignore_errors', False)
    clear_all = request.POST.get('clear_all', False)
    
    if not backup_file:
        return redirect(reverse('setting'))
        
    def import_data(zf, model_dataset_map, dry_run=False):
        error = False
        for model, dataset in model_dataset_map.items(): 
            dataset = tablib.import_set(zf.read(dataset))
            data = model().import_data(dataset, dry_run=dry_run)
            error = error or data.has_errors()
        return error
        
    def import_files(zf):
        for f in zf.infolist():
            if f.filename.startswith(media_root_base):
                zf.extract(f, os.path.dirname(settings.MEDIA_ROOT))
                
    def delete_data():
        Event.objects.all().delete()
        Person.objects.all().delete()
        Tag.objects.all().delete()
        Attachment.objects.all().delete()
        
    def delete_files():
        shutil.rmtree(settings.EVENT_IMAGES_DIR, ignore_errors=True)
        shutil.rmtree(settings.PERSON_IMAGES_DIR, ignore_errors=True)
        shutil.rmtree(settings.EVENT_ATTACHMENTS_DIR, ignore_errors=True)
        if not os.path.exists(settings.EVENT_IMAGES_DIR): os.makedirs(settings.EVENT_IMAGES_DIR)
        if not os.path.exists(settings.PERSON_IMAGES_DIR): os.makedirs(settings.PERSON_IMAGES_DIR)
        if not os.path.exists(settings.EVENT_ATTACHMENTS_DIR): os.makedirs(settings.EVENT_ATTACHMENTS_DIR)
        
    try:
        zf = zipfile.ZipFile(backup_file)
                
        model_dataset_map = {
            TagResource: 'tags.csv',
            PersonResource: 'persons.csv',
            EventResource: 'events.csv',
            AttachmentResource: 'attachments.csv' 
        }
        
        if not ignore_errors and import_data(zf, model_dataset_map, True):
            return redirect(reverse('setting') + "?restore_error=1")
        else:
            if clear_all:
                delete_files()
                delete_data()
            import_files(zf)
            import_data(zf, model_dataset_map, False)
            import_data(zf, model_dataset_map, False) # Save twice to take care of foreign (m2m, etc.) relations.
    except:
        return redirect(reverse('setting') + "?restore_error=1")
        
    return redirect(reverse('setting') + "?restore_success=1")