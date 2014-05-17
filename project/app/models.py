from django.db import models
import jdatetime

class Event(models.Model):
    class Meta: db_table = "Event"
    subject = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=1000)
    date_happened = models.DateTimeField()
    date_ended = models.DateTimeField(null=True, blank=True)
    photo = models.CharField(max_length=1000, null=True, blank=True)
    actions_taken = models.TextField(null=True, blank=True)
    persons = models.ManyToManyField("Person", null=True, blank=True, db_table="Event_Person")
    tags = models.ManyToManyField('Tag', null=True, blank=True, related_name="events", db_table="Event_Tag")
    related_events = models.ManyToManyField("self", null=True, blank=True, db_table="Event_Event")
    status = models.CharField(max_length=15, blank=True, default='public', choices=[('public', 'public'), ('unconfirmed', 'unconfirmed'), ('hidden', 'hidden')])
        
    def __unicode__(self):
        return "%s (%s)" % (self.subject, self.location)
        
    @property
    def jalali_date_happened(self):
        try: return jdatetime.date.fromgregorian(date=self.date_happened.date())
        except: return self.date_happened
        
    @property
    def jalali_date_ended(self):
        try: return jdatetime.date.fromgregorian(date=self.date_ended.date())
        except: return self.date_ended
        
    @property
    def tags_string(self):
        return ", ".join([unicode(t) for t in self.tags.all()])
        
    @property
    def persons_string(self):
        return ", ".join([unicode(p) for p in self.persons.all()])
        
    @property
    def truncated_description(self):
        import re
        s = re.sub(r'(<!--.*?-->|<[^>]*>)', '', self.description)
        width = 300
        if len(s) <= 300:
            return s
        else:
            if s[width].isspace():
                return s[0:width] + "...";
            else:
                return s[0:width].rsplit(None, 1)[0] + "..."

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
    events = models.ManyToManyField("Event", null=True, blank=True, db_table="Event_Person")
    status = models.CharField(max_length=15, blank=True, default='public', choices=[('public', 'public'), ('unconfirmed', 'unconfirmed'), ('hidden', 'hidden')])
        
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
                
class Tag(models.Model):
    class Meta: db_table = "Tag"
    name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name
    
class Attachment(models.Model):
    class Meta: db_table = "Attachment"
    name = models.CharField(max_length=255)
    filename = models.CharField(max_length=1000, unique=True)
    event = models.ForeignKey("Event", related_name="attachments")
    
    def __unicode__(self):
        return self.name
