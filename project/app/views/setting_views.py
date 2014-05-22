#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import os
import zipfile
import tablib
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

from app.resources import *

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
    with zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('events.csv', events)
        zf.writestr('persons.csv', persons)
        zf.writestr('tags.csv', tags)
        zf.writestr('attachments.csv', attachments)
        
        if include_files:
            for dirname, subdirs, files in os.walk(settings.MEDIA_ROOT):
                for filename in files:
                    source = os.path.join(dirname, filename)
                    destination = os.path.join(os.path.basename(settings.MEDIA_ROOT), os.path.basename(dirname), filename)
                    zf.write(source, destination)
                       
    response = HttpResponse(content_type=' application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="Backup_%s.zip"' % datetime.now().strftime("%Y_%m_%d")
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response    
    
@login_required
def setting_restore(request, *args, **kwargs):       
    backup_file = request.FILES.get('backup_file', None)
    
    if not backup_file:
        return redirect(reverse('setting'))
        
    try:
        zf = zipfile.ZipFile(backup_file)
        
        events_dataset = tablib.import_set(zf.read('events.csv'))
        persons_dataset = tablib.import_set(zf.read('persons.csv'))
        tagst_dataset = tablib.import_set(zf.read('tags.csv'))
        attachments_dataset = tablib.import_set(zf.read('attachments.csv'))
        
        events = EventResource().import_data(events_dataset, dry_run=True)
        persons = PersonResource().import_data(persons_dataset, dry_run=True)
        tags = TagResource().import_data(tagst_dataset, dry_run=True)
        attachments = AttachmentResource().import_data(attachments_dataset, dry_run=True)
        
        if events.has_errors() or persons.has_errors() or tags.has_errors() or attachments.has_errors():
            return redirect(reverse('setting') + "?restore_error=1")
        else:
            pass
            events = EventResource().import_data(events_dataset)
            persons = PersonResource().import_data(persons_dataset)
            tags = TagResource().import_data(tagst_dataset)
            attachments = AttachmentResource().import_data(attachments_dataset)
            
        for f in zf.infolist():
            if f.filename.startswith('media'):
                zf.extract(f, os.path.dirname(settings.MEDIA_ROOT))
    except:
        return redirect(reverse('setting') + "?restore_error=1")
        
    return redirect(reverse('setting') + "?restore_success=1")