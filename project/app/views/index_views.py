#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from app.models import *

def index_view(request, *args, **kwargs):
    try: events = Event.objects.filter(status='public').order_by("-date_happened")
    except: events = None
    event = events[0] if events else None
    events = events[1:10] if len(events) > 1 else None
    return render_to_response('index.html', locals(), context_instance = RequestContext(request))