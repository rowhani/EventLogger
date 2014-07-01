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
from app.utils import *
    
def calendar_view(request, *args, **kwargs):
    active_link_id = "calendar"
    
    mode = request.GET.get("mode", "monthly")
    year = request.GET.get('year', 0)
    month = request.GET.get('month', 0)
    day = request.GET.get('day', 0)
    
    all_dates = []        
    yr = []
    months = []
    for i in range(12):
        mnt = []
        zeros = 0
        for j in range(5):
            week = []
            for k in range(1, 8):
                day_of_month = j * 7 + k
                day_of_year = sum(months if months else [0]) + day_of_month
                if (i < 6 and day_of_month > 31) or (i >= 6 and day_of_month > 30): 
                    day_of_year = 0
                    zeros += 1
                daystr = to_persian_digits(day_of_month)             
                week.append([day_of_year, daystr])
            mnt.append(week)
        months.append(day_of_month - zeros)
        yr.append([month_names[i], mnt])
    row = []
    for i, mnt in enumerate(yr):
        if (i + 1) % 3 == 0: 
            row.append(mnt)
            all_dates.append(row)
            row = []
        else:
            row.append(mnt)            

    return render_to_response('calendar.html', locals(), context_instance = RequestContext(request))
    
def calendar_monthly_events(request, *args, **kwargs):
    mode = request.GET.get("mode", "monthly")
    start_date = jdatetime.datetime.strptime("%s/%s/1" % (request.GET['year'], request.GET['month']), '%Y/%m/%d').togregorian() + relativedelta(days=-6)
    end_date = start_date + relativedelta(days=36 if mode == 'monthly' else 372)
    events = Event.objects.filter(status='public', date_happened__gte=start_date, date_happened__lte=end_date)
    event_map = {}
    for event in events:
        date = event.date_happened.strftime("%Y/%m/%d")
        data = {"subject": event.subject.encode('utf-8', 'ignore'), "url": reverse("detail_event", args=[event.id])}
        if date in event_map: event_map[date].append(data)
        else: event_map[date] = [data]
        
    return HttpResponse(json.dumps(event_map))
    
def calendar_total_events(request, *args, **kwargs):
    events = Event.objects.filter(status='public').order_by("-date_happened")
    event_map = {}
    for event in events:
        jdate = jdatetime.datetime.fromgregorian(datetime=event.date_happened)
        date = int(jdate.strftime('%j'))
        data = {"subject": "%s (%s)" % (event.subject.encode('utf-8', 'ignore'), to_persian_digits(jdate.strftime('%Y'))), "url": reverse("detail_event", args=[event.id])}
        if date in event_map: event_map[date].append(data)
        else: event_map[date] = [data]
        
    return HttpResponse(json.dumps(event_map))