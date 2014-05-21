#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import jdatetime
import re
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.conf import settings
from django.db.models import Q

from app.models import *
from app.utils import *
    
def search_view(request, *args, **kwargs):
    active_link_id = "search"
    
    query = request.GET.get('query', '')
    tags = request.GET.getlist('tags[]')
    persons = request.GET.getlist('persons[]')
    status = request.GET.getlist('status[]')
    date_range = request.GET.get('date_range', '')
    type = request.GET.get('type', '')
    stage = request.GET.get('stage', '')    
    subject = request.GET.get('subject', '')
    location = request.GET.get('location', '')
    description = request.GET.get('description', '')
    if subject or location or description: query = ''
    
    all_tags = Tag.objects.all()
    tags_json = json.dumps(tags)
    
    all_persons = Person.objects.all()
    persons_json = json.dumps(persons)
        
    status_json = json.dumps(status)
    
    subject_keywords = json.dumps(get_keywords(subject or query))
    description_keywords = json.dumps(get_keywords(description or query))
    location_keywords = json.dumps(get_keywords(location or query))
        
    return render_to_response('search.html', locals(), context_instance = RequestContext(request))    
    
class SearchResultJson(BaseDatatableView):
    model = Event
    columns = ['all']
    max_display_length = 50    
    
    def render_column(self, row, column):  
        if column == 'all':
            query = self.request.GET.get('description', '') or self.request.GET.get('query', '')
            resp = """
                <div class="col-lg-1">
                    <a href="%(detail_url)s">
                        <span class="thumbnail" style="margin-bottom: 5px;">                           
                            %(photo)s
                        </span>
                    </a>
                </div>""" % {
                    "detail_url": reverse('detail_event', args=[row.id]),
                    "photo": ('<img src="%s%s"/>' % (settings.EVENT_IMAGES_URL, row.photo)).encode('utf-8', 'ignore') if row.photo else '<span class="fa fa-picture-o fa-lg"></span>' 
                }
            resp += """
                <div class="col-lg-11">
                    <h4 class="event-subject"><a href="%(detail_url)s">%(subject)s</a></h4>
                    <span class="event-date convert-date">%(date)s</span> در <strong class="event-location">%(location)s</strong> - 
                    <span class="event-description">%(description)s</span>
                </div>""" % {
                    "detail_url": reverse('detail_event', args=[row.id]),
                    "subject": row.subject.encode('utf-8', 'ignore'),
                    "date": row.date_happened,
                    "location": row.location.encode('utf-8', 'ignore'),
                    "description": get_truncated_text(row.description_raw, get_keywords(query)).encode('utf-8', 'ignore')
                }
            return resp
                
    def filter_queryset(self, qs):
        query = self.request.GET.get('query', '')
        tags = self.request.GET.getlist('tags[]')
        persons = self.request.GET.getlist('persons[]')
        status = self.request.GET.getlist('status[]') 
        date_range = self.request.GET.get('date_range', '')
        type = self.request.GET.get('type', '')
        stage = self.request.GET.get('stage', '')
        subject = self.request.GET.get('subject', '')
        location = self.request.GET.get('location', '')
        description = self.request.GET.get('description', '')
        if subject or location or description: query = ''
                
        if status: qs = qs.filter(status__in=status)
        
        if tags: qs = qs.filter(tags__in=tags)  
        
        if persons: qs = qs.filter(persons__in=persons)
        
        if type == 'personal': qs = qs.exclude(persons=None)
        elif type == 'general': qs = qs.filter(persons=None)
        
        if stage == 'finished': qs = qs.exclude(date_ended=None)
        elif stage == 'current': qs = qs.filter(date_ended=None)
        
        try:
            dates = [jdatetime.datetime.strptime(date.strip(), '%Y/%m/%d').togregorian() for date in date_range.split("-")]
            dates.sort()
            qs = qs.filter(date_happened__gte=dates[0], date_happened__lte=dates[1])
        except:
            pass
        
        if query:
            keywords = get_keywords(query)
            expr = Q()
            for kw in keywords: expr = expr|Q(subject__icontains=kw)|Q(location__icontains=kw)|Q(description_raw__icontains=kw)
            qs = qs.filter(expr)
        else:
            if subject: 
                keywords = get_keywords(subject)
                expr = Q()
                for kw in keywords: expr = expr|Q(subject__icontains=kw)
                qs = qs.filter(expr)
            if location: 
                keywords = get_keywords(location)
                expr = Q()
                for kw in keywords: expr = expr|Q(location__icontains=kw)
                qs = qs.filter(expr)
            if description: 
                keywords = get_keywords(description)
                expr = Q()
                for kw in keywords: expr = expr|Q(description_raw__icontains=kw)
                qs = qs.filter(expr)
        return qs
        
    def get_initial_queryset(self):
        return super(SearchResultJson, self ).get_initial_queryset().order_by("-date_happened")
        
    def prepare_results(self, qs):
        return super(SearchResultJson, self ).prepare_results(qs)
