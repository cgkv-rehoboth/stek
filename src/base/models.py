from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from livefield.models import LiveModel
from django.db.models import Count

import os

class Slide(LiveModel, models.Model):

  image       = models.CharField(max_length=255)
  title       = models.CharField(max_length=255)
  description = models.TextField(blank=True, null=True)
  owner       = models.ForeignKey(User)

  def __str__(self): return self.title

class Address(models.Model):

  street      = models.CharField(max_length=255, blank=True)
  zip         = models.CharField(max_length=6, blank=True)
  city        = models.CharField(max_length=255, blank=True)
  country     = models.CharField(max_length=255, default="Nederland")
  phone       = models.CharField(max_length=15, blank=True)

  def __str__(self):
    return "%s, %s, %s (%s)" % (self.street, self.zip, self.city, self.country)

def user_profile_pic(profile, filename):
  _, ext = os.path.splitext(filename)

  return 'profiles/%s.%s' % (profile.username, ext)

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
  birthday    = models.DateField()
  photo       = models.ImageField(upload_to=user_profile_pic, null=True, blank=True)
  family      = models.ForeignKey("Family", null=True, related_name='members')
  role_in_family = models.CharField(max_length=3, choices=ROLE_CHOICES, default=KID, null=True)

  def is_favorite_for(self, user):
    return self.favorited_by.filter(owner=user).exists()

  def __str__(self):
    return "Profiel van %s" % (self.user.username)

def family_pic(fam, filename):
  _, ext = os.path.splitext(filename)

  return 'families/%s%s' % (fam.pk, ext)

class Family(models.Model):

  lastname    = models.CharField(max_length=255)
  photo       = models.FileField(upload_to=family_pic, null=True, blank=True) #Todo: specify upload dir
  address     = models.OneToOneField(Address, null=True, blank=True)

  def __str__(self):
    return "Familie %s" % (self.lastname,)

  def size(self):
    return self.members.all().count()

class Favorites(models.Model):

  owner       = models.ForeignKey(Profile, related_name="favorites")
  favorite    = models.ForeignKey(Profile, related_name="favorited_by")
