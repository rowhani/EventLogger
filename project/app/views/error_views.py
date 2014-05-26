#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response

def error_404_view(request, *args, **kwargs):
    return render_to_response('error/404.html', locals(), context_instance = RequestContext(request))

def error_500_view(request, *args, **kwargs):
    return render_to_response('error/500.html', locals(), context_instance = RequestContext(request))