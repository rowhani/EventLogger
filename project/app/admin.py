from django.contrib import admin
from import_export.admin import ImportExportMixin

from app.models import *

class PersonAdmin(ImportExportMixin, admin.ModelAdmin): pass
admin.site.register(Person, PersonAdmin)

class EventAdmin(ImportExportMixin, admin.ModelAdmin): pass
admin.site.register(Event, EventAdmin)

class TagAdmin(ImportExportMixin, admin.ModelAdmin): pass
admin.site.register(Tag, TagAdmin)

class AttachmentAdmin(ImportExportMixin, admin.ModelAdmin): pass
admin.site.register(Attachment, AttachmentAdmin)