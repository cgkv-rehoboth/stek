from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from livefield.models import LiveModel
from django.db.models import Count

# Import models of base app
#from ..base.models import Profile
from base.models import Profile

class TimestampedModel(models.Model):

  class Meta:
    abstract = True

  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

class Timetable(TimestampedModel, LiveModel, models.Model):

  title       = models.CharField(max_length=255)
  owner       = models.ForeignKey(Profile)
  description = models.TextField(blank=True, null=True)
  team        = models.ForeignKey("Team", related_name="timetables", blank=True, null=True)
  incalendar  = models.BooleanField(default=True)
  color       = models.CharField(max_length=6, default='268bd2')

  def __str__(self): return self.title

class Event(TimestampedModel, LiveModel, models.Model):

  incalendar      = models.BooleanField(default=True)
  title           = models.CharField(max_length=255, blank=True, null=True)
  startdatetime   = models.DateTimeField()
  enddatetime     = models.DateTimeField(blank=True, null=True)
  owner           = models.ForeignKey(Profile, related_name="events")
  timetable       = models.ForeignKey(Timetable, related_name="events")
  description     = models.TextField(blank=True, null=True)

  def save(self, *args, **kwargs):
    # default enddate if not set
    if self.enddatetime == None:
      self.enddatetime = self.startdatetime

    super().save(*args, **kwargs)

  def __str__(self):
    return "%s, at %s" % (self.title, self.startdatetime)

class TimetableDuty(models.Model):

  responsible = models.ForeignKey(Profile, related_name="duties")
  event       = models.ForeignKey(Event, related_name="duties")
  timetable   = models.ForeignKey(Timetable, related_name="duties")
  comments    = models.TextField(blank=True, null=True)

  def __str__(self):
    return "%s op %s door %s" % (self.event.title, self.event.startdatetime, self.responsible.profile.name())

class Service(Event):

  minister    = models.CharField(max_length=255)
  theme       = models.CharField(max_length=255, blank=True, default="")
  comments    = models.TextField(blank=True, null=True)

  def save(self, *args, **kwargs):
    if self.title == "": self.title = "Dienst"

    super(Service, self).save(*args, **kwargs)

class Team(models.Model):

  name = models.CharField(max_length=255)
  members = models.ManyToManyField(Profile, through="TeamMember", related_name="members")
  email = models.EmailField(max_length=255, blank=True)
  description = models.TextField(blank=True)

  def __str__(self):
    return "%s" % self.name

  def size(self):
    return self.members.all().count()

  def leaders(self):
    return self.teammembers.filter(role='LEI')

class TeamMember(models.Model):

  LEADER = 'LEI'
  LID = 'LID'

  ROLE_CHOICES = (
    (LEADER, 'leiding'),
    (LID, 'lid'),
  )

  team = models.ForeignKey(Team, related_name="teammembers")
  profile = models.ForeignKey(Profile, related_name="team_membership")
  role = models.CharField(max_length=3, choices=ROLE_CHOICES, default=LID)

  def __str__(self):
    return "%s %s: %s" % (self.team.name, self.get_role_display(), self.user.username)

class RuilRequest(models.Model):

  timetableduty   = models.ForeignKey(TimetableDuty, related_name="ruilen")
  profile         = models.ForeignKey(Profile, related_name="ruilen")
  comments        = models.TextField(blank=True)

  class Meta:
    unique_together = (("timetableduty", "profile"),)
