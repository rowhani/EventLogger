from import_export import resources

from app.models import *

class EventResource(resources.ModelResource):
    class Meta: model = Event
    
class PersonResource(resources.ModelResource):
    class Meta: model = Person
    
class TagResource(resources.ModelResource):
    class Meta: model = Tag
    
class AttachmentResource(resources.ModelResource):
    class Meta: model = Attachment