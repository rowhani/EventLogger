#! /usr/bin/env python2.7
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib import admin
from project.app.models import *
from project.app.views import *

# admin

class PersonAdmin(admin.ModelAdmin): pass
admin.site.register(Person, PersonAdmin)

class LocationAdmin(admin.ModelAdmin): pass
admin.site.register(Location, LocationAdmin)

class EventAdmin(admin.ModelAdmin): pass
admin.site.register(Event, EventAdmin)

class TagAdmin(admin.ModelAdmin): pass
admin.site.register(Tag, TagAdmin)

class AttachmentAdmin(admin.ModelAdmin): pass
admin.site.register(Attachment, AttachmentAdmin)  

admin.autodiscover()

# patterns

urlpatterns = patterns('',
    # Pages:
    url(r'^$', index_view, name='index'),
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout$', logout_view, name='logout'),

    # static
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve,
        {'show_indexes': True, 'insecure': False}),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
)
