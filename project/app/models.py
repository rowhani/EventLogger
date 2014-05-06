from django.db import models
import jdatetime

class Person(models.Model):
    class Meta: db_table = "Person"
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, blank=False, choices=[('male', 'مرد'), ('female', 'زن')])
    birth_date = models.DateTimeField(null=True, blank=True)
    birth_place = models.CharField(max_length=1000, null=True, blank=True)
    death_date = models.DateTimeField(null=True, blank=True)
    death_place = models.CharField(max_length=1000, null=True, blank=True)
    person_photo = models.CharField(max_length=1000, null=True, blank=True)
        
    def __unicode__(self):
        if self.birth_place:
            return "%s %s (%s)" % (self.first_name, self.last_name, self.birth_place)
        else: 
            return "%s %s" % (self.first_name, self.last_name)
            
    @property
    def jalali_birth_date(self):
        try: return jdatetime.date.fromgregorian(date=self.birth_date.date())
        except: return self.birth_date
        
    @property
    def jalali_death_date(self):
        try: return jdatetime.date.fromgregorian(date=self.death_date.date())
        except: return self.death_date
            
class Event(models.Model):
    class Meta: db_table = "Event"
    subject = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=1000)
    date_happened = models.DateTimeField()
    date_ended = models.DateTimeField(null=True, blank=True)
    photo = models.CharField(max_length=1000, null=True, blank=True)
    person = models.ForeignKey("Person", null=True, blank=True, related_name="events")
    actions_taken = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', through='EventTags', null=True, blank=True)
    related_events = models.ManyToManyField("self", null=True, blank=True)
        
    def __unicode__(self):
        if self.jalali_date_happened:
            return "%s - %s (%s)" % (self.subject, self.location, self.jalali_date_happened.strftime("%d/%m/%Y"))
        else:
            return "%s - %s" % (self.subject, self.location)
        
    @property
    def jalali_date_happened(self):
        try: return jdatetime.date.fromgregorian(date=self.date_happened.date())
        except: return self.date_happened
        
    @property
    def jalali_date_ended(self):
        try: return jdatetime.date.fromgregorian(date=self.date_ended.date())
        except: return self.date_ended
    
class Tag(models.Model):
    class Meta: db_table = "Tag"
    name = models.CharField(max_length=100, unique=True)
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
    filename = models.CharField(max_length=1000, unique=True)
    event = models.ForeignKey("Event", related_name="attachments")
    
    def __unicode__(self):
        return self.name
