from django.db import models

class Person(models.Model):
    class Meta: db_table = "Person"
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    birth_date = models.DateTimeField(null=True, blank=True)
    birth_place = models.ForeignKey("Location", null=True, blank=True, related_name="birth_persons") 
    death_date = models.DateTimeField(null=True, blank=True)
    death_place = models.ForeignKey("Location", null=True, blank=True, related_name="death_persons") 
    photo = models.CharField(max_length=1000, null=True, blank=True)
    
    def __unicode__(self):
        return "%s %s" % (slef.first_name, self.last_name)
    
class Location(models.Model):
    class Meta: db_table = "Location"
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    
    def __unicode__(self):
        return "%s %s %s %s" % (slef.country, self.province, self.city, self.address)
    
class Event(models.Model):
    class Meta: db_table = "Event"
    subject = models.CharField(max_length=200)
    description = models.TextField()
    location = models.ForeignKey("Location", null=True, blank=True)
    date_happened = models.DateTimeField()
    date_ended = models.DateTimeField(null=True, blank=True)
    photo = models.CharField(max_length=1000, null=True, blank=True)
    person = models.ForeignKey("Person", null=True, blank=True)
    actions_taken = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', through='EventTags')
    related_events = models.ManyToManyField("self", null=True, blank=True)
    
    def __unicode__(self):
        return "%s - %s - %s" % (slef.subject, self.location, self.date_happened)
    
class Tag(models.Model):
    class Meta: db_table = "Tag"
    name = models.CharField(max_length=50, unique=True)
    events = models.ManyToManyField('Event', through='EventTags')
    
    def __unicode__(self):
        return self.name
    
class EventTags(models.Model):
    class Meta: db_table = "EventTags"
    event = models.ForeignKey("Event")
    tag = models.ForeignKey("Tag")
    
    def __unicode__(self):
        return "%s - %s" % (self.event, self.tag)
    
class Attachment(models.Model):
    class Meta: db_table = "Attachment"
    name = models.CharField(max_length=255)
    filename = models.CharField(max_length=255, unique=True)
    event = models.ForeignKey("Event", related_name="attachments")
    
    def __unicode__(self):
        return self.name
