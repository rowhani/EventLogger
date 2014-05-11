#! /usr/bin/env python2.7
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from project.app.models import *
from project.app.views import *

# admin

class PersonAdmin(admin.ModelAdmin): pass
admin.site.register(Person, PersonAdmin)

class EventAdmin(admin.ModelAdmin): pass
admin.site.register(Event, EventAdmin)

class TagAdmin(admin.ModelAdmin): pass
admin.site.register(Tag, TagAdmin)

class AttachmentAdmin(admin.ModelAdmin): pass
admin.site.register(Attachment, AttachmentAdmin)  

admin.autodiscover()

# error handling

handler404 = 'app.views.error_404_view'
handler500 = 'app.views.error_500_view'

# patterns

urlpatterns = patterns('',
    # views:
    url(r'^$', index_view, name='index'),
    
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout$', logout_view, name='logout'),
    
    url(r'^event$', list_event_view, name='list_event'),
    url(r'^event/json/$', EventListJson.as_view(), name='list_event_json'),
    url(r'^event/(?P<event_id>\d+)$', detail_event_view, name='detail_event'),
    url(r'^event/add$', modify_event_view, name='add_event'),
    url(r'^event/edit/(?P<event_id>\d+)$', modify_event_view, name='edit_event'),    
    url(r'^event/delete/(?P<event_id>\d+)$', delete_event_view, name='delete_event'), 
    url(r'^event/change_status/(?P<event_id>\d+)/(?P<status>\w+)$', change_status_event_view, name='change_status_event'), 

    # static
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve, {'show_indexes': True, 'insecure': False}),
    url(r'^captcha/', include('captcha.urls')),
    
    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
)
