from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from livefield.models import LiveModel
from django.db.models import Count
from datetime import datetime
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import unidecode

import os

class Slide(LiveModel, models.Model):

  image       = models.CharField(max_length=255)
  title       = models.CharField(max_length=255)
  description = models.TextField(blank=True, null=True)
  owner       = models.ForeignKey(User) # Todo: replace User with Profile

  def __str__(self): return self.title

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

  # Remove all harmfull chars
  name = ''.join(e for e in unidecode.unidecode(profile.name()) if e.isalnum())

  return 'profiles/%s_%s%s' % (profile.pk, name, ext)

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
  initials    = models.CharField(max_length=64, blank=True, null=True, default="")
  last_name   = models.CharField(max_length=255, blank=True)
  prefix      = models.CharField(max_length=64, blank=True, null=True, default="") # todo: run migration
  email       = models.CharField(max_length=255, blank=True, null=True)
  birthday    = models.DateField(null=True)
  photo       = models.ImageField(upload_to=user_profile_pic, null=True, blank=True)
  family      = models.ForeignKey("Family", null=True, related_name='members')
  role_in_family = models.CharField(max_length=3, choices=ROLE_CHOICES, default=KID, null=True)

  class Meta:
    unique_together = (('first_name', 'last_name', 'birthday'), )

  def save(self, *args, **kwargs):
    # Only update photo if special args are given (the center args)
    if self.photo and args and args[0]:
      # Compress picture
      p = Image.open(self.photo).convert('RGB')

      # Preferred output image size (in pixels)
      prefsize = 400, 400

      ## Choose a option to save the profile picture
      # 1) Scale to max width and height
      #p.thumbnail(prefsize,Image.ANTIALIAS)

      # 2) Scale to max width or height
      #if p.size[0]>p.size[1]:
      #  size = prefsize[0], round(prefsize[1]*p.size[1]/p.size[0])
      #else:
      #  size = round(prefsize[0]*p.size[0]/p.size[1]), prefsize[1]
      #p.resize(size, Image.ANTIALIAS)

      # 3) Cropscale image to max widt and height
      # Get center (if specified)
      center = args[0].split(',')
      center = float(center[0]),float(center[1])
      args = {}

      p = ImageOps.fit(p, prefsize, Image.ANTIALIAS, 0, center)

      # Save
      output = BytesIO()
      p.save(output, format='JPEG', quality=90, optimize=True)
      output.seek(0, os.SEEK_END)
      self.photo = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.photo.name, 'image/jpeg', output.tell(), None)

    super().save(*args, **kwargs)

  def best_address(self):
    if self.address:
      return self.address
    else:
      return self.family.address

  def name(self):
    return "%s %s" % (self.first_name, self.last_namef())

  def namei(self):
    return "%s %s" % (self.initials, self.last_namef())

  def first_namei(self):
    return "%s, %s" % (self.first_name, self.initials)

  def last_namef(self):
    if self.prefix == "":
      return self.last_name
    else:
      return "%s %s" % (self.prefix, self.last_name)

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
