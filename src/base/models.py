from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from livefield.models import LiveModel
from django.db.models import Count
from datetime import datetime

import os

class Slide(LiveModel, models.Model):

  image       = models.CharField(max_length=255)
  title       = models.CharField(max_length=255)
  description = models.TextField(blank=True, null=True)
  owner       = models.ForeignKey(User) # Todo: replace User with Profile

  def __str__(self): return self.title

class Popup(models.Model):

  title           = models.CharField(max_length=255, blank=True, default="")
  content         = models.TextField()
  startdatetime   = models.DateTimeField()  # Todo: set default to today
  enddatetime     = models.DateTimeField()
  islive          = models.BooleanField(default=True)

  def __str__(self):
    return "[%s] %s" % (self.title, self.content)

  def getCurrentVisible(self):
    return self.filter(startdatetime__gte=datetime.today().date(), enddatetime_lte=datetime.today().date(), islive=True)

class Wijk(models.Model):

  id = models.IntegerField(primary_key=True)
  naam = models.CharField(max_length=255)

  def __str__(self):
    return "%s (%s)" % (self.naam, self.id)

class Address(models.Model):

  street      = models.CharField(max_length=255, blank=True)
  zip         = models.CharField(max_length=6, blank=True)
  city        = models.CharField(max_length=255, blank=True)
  country     = models.CharField(max_length=255, default="Nederland")
  phone       = models.CharField(max_length=15, blank=True)
  wijk        = models.ForeignKey(Wijk, null=True, blank=True)

  def __str__(self):
    return "%s, %s, %s (%s)" % (self.street, self.zip, self.city, self.country)

def user_profile_pic(profile, filename):
  _, ext = os.path.splitext(filename)

  return 'profiles/%s_%s%s' % (profile.pk, profile.user.username, ext)

class Profile(models.Model):

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

  user        = models.OneToOneField(User, null=True, blank=True, related_name="profile")
  address     = models.ForeignKey(Address, null=True, blank=True)
  phone       = models.CharField(max_length=15, blank=True)
  first_name  = models.CharField(max_length=255, blank=True)
  last_name   = models.CharField(max_length=255, blank=True)
  email       = models.CharField(max_length=255, blank=True, null=True)
  birthday    = models.DateField(null=True)
  photo       = models.ImageField(upload_to=user_profile_pic, null=True, blank=True)
  family      = models.ForeignKey("Family", null=True, related_name='members')
  role_in_family = models.CharField(max_length=3, choices=ROLE_CHOICES, default=KID, null=True)

  class Meta:
    unique_together = (('first_name', 'last_name', 'birthday'), )

  def best_address(self):
    if self.address:
      return self.address
    else:
      return self.family.address

  def name(self):
    return "%s %s" % (self.first_name, self.last_name)

  def is_favorite_for(self, user):
    return self.favorited_by.filter(owner=user).exists()

  def __str__(self):
    return "Profiel van %s" % self.name()

  def teamleader_of(self, team):
    # Check if user is teamleader of this timetable's team
    if self.team_membership.filter(team=team, profile=self).exists():
      return self.team_membership.filter(team=team, profile=self).first().role == 'LEI'
    else:
      return False

def family_pic(fam, filename):
  _, ext = os.path.splitext(filename)

  return 'families/%s%s' % (fam.pk, ext)

class Family(models.Model):

  lastname    = models.CharField(max_length=255)
  photo       = models.FileField(upload_to=family_pic, null=True, blank=True) #Todo: specify upload dir
  address     = models.OneToOneField(Address, null=True, blank=True, related_name="family")

  def __str__(self):
    return "Familie %s" % (self.lastname,)

  def size(self):
    return self.members.all().count()

class Favorites(models.Model):

  owner       = models.ForeignKey(Profile, related_name="favorites")
  favorite    = models.ForeignKey(Profile, related_name="favorited_by")
