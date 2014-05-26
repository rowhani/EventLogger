#! /usr/bin/env python2.7
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

class TagForm(ModelForm):
    class Meta:
        model = Tag 
        labels = {
            'name': 'نام دسته'
        }
 
######## Views ########

def list_tag_view(request, *args, **kwargs):
    active_link_id = "tag"
    
    tags = Tag.objects.all()
    
    return render_to_response('tag/list.html', locals(), context_instance = RequestContext(request))
       
@login_required
def delete_tag_view(request, tag_id, *args, **kwargs):
    tag = get_object_or_404(Tag, pk=int(tag_id))
    tag.delete()
    return redirect(reverse('list_tag'))
   
@login_required
def modify_tag_view(request, tag_id=None, *args, **kwargs):
    active_link_id = "tag"    
    
    if tag_id:
        action = reverse('edit_tag', args=[tag_id])
        tag_instance = get_object_or_404(Tag, pk=int(tag_id))
        title = "ویرایش دسته"
    else:
        action = reverse('add_tag')
        tag_instance = None
        title = "ایجاد دسته"
        
    if request.method == 'POST': 
        tag_form = TagForm(request.POST, request.FILES, instance=tag_instance, auto_id='%s')
        if tag_form.is_valid():
            tag = tag_form.save()  
            return close_modal(reverse('list_tag'))
    else:
        tag_form = TagForm(instance=tag_instance, auto_id='%s')                            
                
    return render_to_response('tag/modify.html', locals(), context_instance = RequestContext(request))
    