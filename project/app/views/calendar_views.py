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
    
def calendar_view(request, *args, **kwargs):
    active_link_id = "calendar"
    
    mode = request.GET.get("mode", "monthly")
    year = request.GET.get('year', 0)
    month = request.GET.get('month', 0)
    day = request.GET.get('day', 0)

    return render_to_response('calendar.html', locals(), context_instance = RequestContext(request))
    
def calendar_monthly_events(request, *args, **kwargs):
    mode = request.GET.get("mode", "monthly")
    start_date = jdatetime.datetime.strptime("%s/%s/1" % (request.GET['year'], request.GET['month']), '%Y/%m/%d').togregorian() + relativedelta(days=-6)
    end_date = start_date + relativedelta(days=36 if mode == 'monthly' else 372)
    events = Event.objects.filter(status='public', date_happened__gte=start_date, date_happened__lte=end_date)
    event_map = {}
    for event in events:
        date = event.date_happened.strftime("%Y/%m/%d")
        if date in event_map: event_map[date].append(event.subject.encode('utf-8', 'ignore'))
        else: event_map[date] = [{"subject": event.subject.encode('utf-8', 'ignore'), "url": reverse("detail_event", args=[event.id])}]
    return HttpResponse(json.dumps(event_map))
    