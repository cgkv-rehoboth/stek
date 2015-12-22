from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from livefield.models import LiveModel
from django.db.models import Count

class TimestampedModel(models.Model):

  class Meta:
    abstract = True

  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

class Timetable(TimestampedModel, LiveModel, models.Model):

  title       = models.CharField(max_length=255)
  owner       = models.ForeignKey(User)
  description = models.TextField(blank=True, null=True)
  team        = models.ForeignKey(Team, related_name="timetables", null=True)

  def __str__(self): return self.title

class Event(TimestampedModel, LiveModel, models.Model):

  # detail object can be any model implementing EventDetails
  incalendar      = models.BooleanField(default=True)
  title           = models.CharField(max_length=255, blank=True, null=True)
  startdatetime   = models.DateTimeField()
  enddatetime     = models.DateTimeField(blank=True, null=True)
  owner           = models.ForeignKey(User, related_name="events")
  timetable       = models.ForeignKey(Timetable, related_name="events")
  description     = models.TextField(blank=True, null=True)

  # minutes; null = not repeated
  repeatEvery = models.IntegerField(blank=True, null=True, default=None)

  def __str__(self): return self.title

class TimetableDuty(models.Model):

  responsible = models.ForeignKey(User, related_name="duties")
  event       = models.ForeignKey(Event, related_name="duties")
  timetable   = models.ForeignKey(Timetable, related_name="duties")
  comments    = models.TextField(blank=True, null=True)

  def __str__(self):
    self.title = "%s (%s)" % (self.timetable.title, self.responsible)

    return "%s op %s: %s" % (self.timetable.title, self.event.datetime, self.responsible)

class Service(models.Model):

  minister    = models.CharField(max_length=255)
  theme       = models.CharField(max_length=255, blank=True, default="")
  event       = models.ForeignKey(Event)
  timetable   = models.ForeignKey(Timetable, related_name="services")
  comments    = models.TextField(blank=True, null=True)

  def save(self, *args, **kwargs):
    self.title = "Dienst (%s)" % self.minister
    if self.theme != "": self.title += ": %s" % self.theme

    super(Service, self).save(*args, **kwargs)


class Team(models.Model):

  name = models.CharField(max_length=255)
  members = models.ManyToManyField(User, through="TeamMember")

  def __str__(self):
    return "Team %s" % self.name

  def size(self):
    return self.members.all().count()

class TeamMember(models.Model):

  LEADER = 'LEI'
  LID = 'LID'

  ROLE_CHOICES = (
    (LEADER, 'Leiding'),
    (LID, 'Leden'),
  )

  team = models.ForeignKey(Team)
  user = models.ForeignKey(User)
  role = models.CharField(max_length=3, choices=ROLE_CHOICES, default=LID)
  email = models.EmailField(max_length=255, blank=True)
  description = models.TextField(blank=True)


  def __str__(self):
    return "%s %s: %s" % (self.team.name, self.get_role_display(), self.user.username)
