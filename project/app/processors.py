import jdatetime
import json
import re
from django.conf import settings
from django.core.urlresolvers import reverse

from app.models import *

def settings_context(context):
    return settings._wrapped.__dict__

def calendar_context(context):
    month_names = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
    persian_numbers = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'};
    urls = []
    now = jdatetime.datetime.now().date().replace(day=1)
    year = "".join([persian_numbers[num] for num in str(now.year)])
    for i in range(1, 13):
        start = now.replace(month = i)
        urls.append(reverse("calendar") + "?year=%s&month=%s" % (start.strftime("%Y"), start.strftime("%m")))
    month_names = ["%s %s" % (m, year) for m in month_names]
    calendar_months = zip(month_names, urls) 
    return {"calendar_months" : json.dumps(calendar_months)}
    
def recent_events_processor(context):
    events = Event.objects.filter(status='public').order_by("-date_happened")[:5]
    events = [(event.subject, event.date_happened.strftime("%Y/%m/%d"), reverse('detail_event', args=[event.id])) for event in events]
    return {"recent_events": json.dumps(events)}
    