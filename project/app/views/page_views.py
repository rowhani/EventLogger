#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required

@login_required
def index_view(request, *args, **kwargs):
    active_link_id = "home"
    return render_to_response('index.html', locals(), context_instance = RequestContext(request))