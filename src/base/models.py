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

class Slide(LiveModel, models.Model):

  image       = models.CharField(max_length=255)
  title       = models.CharField(max_length=255)
  description = models.TextField(blank=True, null=True)
  owner       = models.ForeignKey(User)

  def __str__(self): return self.title

class Timetable(TimestampedModel, LiveModel, models.Model):

  incalendar  = models.BooleanField(default=True)
  title       = models.CharField(max_length=255)
  owner       = models.ForeignKey(User)
  description = models.TextField(blank=True, null=True)

  def __str__(self): return self.title

class Event(TimestampedModel, LiveModel, models.Model):

  # detail object can be any model implementing EventDetails
  title       = models.CharField(max_length=255, blank=True)
  datetime    = models.DateTimeField()
  owner       = models.ForeignKey(User)
  timetable   = models.ForeignKey(Timetable, related_name="events")

  # minutes; null = not repeated
  repeatEvery = models.IntegerField(blank=True, null=True, default=None)

  def __str__(self): return self.title

class Service(Event):

  minister    = models.CharField(max_length=255)
  theme       = models.CharField(max_length=255, blank=True, default="")

  def save(self, *args, **kwargs):
    self.title = "Dienst (%s)" % self.minister
    if self.theme != "": self.title += ": %s" % self.theme

    super(Service, self).save(*args, **kwargs)

class TimetableDuty(Event):

  responsible = models.ForeignKey(User)

  def __str__(self):
    self.title = "%s (%s)" % (self.timetable.title, self.responsible)

    return "%s op %s: %s" % (self.timetable.title, self.datetime, self.responsible)

class Address(models.Model):

  street      = models.CharField(max_length=255, blank=True)
  zip         = models.CharField(max_length=6, blank=True)
  city        = models.CharField(max_length=255, blank=True)
  country     = models.CharField(max_length=255, default="Nederland")

class Profile(models.Model):

  user        = models.ForeignKey(User, null=True, blank=True)
  address     = models.ForeignKey(Address, null=True, blank=True)
  phone       = models.CharField(max_length=15, blank=True)
  birthday    = models.DateField()

  def __str__(self):
    return "Profiel van %s" % (self.user.username)

class Family(models.Model):

  lastname = models.CharField(max_length=255)
  members = models.ManyToManyField(Profile, through="FamilyMember")

  def __str__(self):
    return "Familie %s" % self.lastname

  def size(self):
    return self.members.all().count()

class FamilyMember(models.Model):

  DAD = 'DAD'
  MUM = 'MUM'
  KID = 'KID'
  INDEPENDENT_KID = 'IKI'

  ROLE_CHOICES = (
    (DAD, 'Father'),
    (MUM, 'Mother'),
    (KID, 'Kid'),
    (INDEPENDENT_KID, 'Independent kid'),
  )

  family = models.ForeignKey(Family)
  profile = models.ForeignKey(Profile)
  role = models.CharField(max_length=3, choices=ROLE_CHOICES, default=KID)

  def __str__(self):
    return "%s %s: %s" % (self.family.lastname, self.get_role_display(), self.profile.user.username)
