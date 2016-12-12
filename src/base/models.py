from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from livefield.models import LiveModel
from django.db.models import Count
from datetime import datetime
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from itertools import chain
import unidecode

import os
from agenda.models import *

class Slide(LiveModel, models.Model):

  image       = models.CharField(max_length=255)
  title       = models.CharField(max_length=255)
  description = models.TextField(blank=True, null=True)
  owner       = models.ForeignKey(User) # Todo: replace User with Profile

  def __str__(self): return self.title

class Wijk(models.Model):

  id = models.IntegerField(primary_key=True)
  naam = models.CharField(max_length=255)

  class Meta:
    ordering = ('id',)

  def __str__(self):
    return "%s (%s)" % (self.naam, self.id)

class Address(models.Model):

  street      = models.CharField(max_length=255, blank=True)
  zip         = models.CharField(max_length=6, blank=True)
  city        = models.CharField(max_length=255, blank=True)
  country     = models.CharField(max_length=255, default="Nederland")
  phone       = models.CharField(max_length=15, blank=True)
  wijk        = models.ForeignKey(Wijk, null=True, blank=True)

  class Meta:
    ordering = ('street', 'city',)

  def __str__(self):
    return "%s, %s, %s (%s)" % (self.street, self.zip, self.city, self.country)

  def occupant(self):
    if self.family:
      return self.family
    else:
      return self.profile

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
  address     = models.ForeignKey(Address, null=True, blank=True, related_name="profile")
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
  has_logged_in  = models.NullBooleanField(default=False, null=True)

  class Meta:
    unique_together = (('first_name', 'last_name', 'birthday'), )

  def delete(self, *args, **kwargs):
    # remove all ruilrequests
    RuilRequest.objects.filter(profile=self).delete()
    super().delete(*args, **kwargs)

  def check_firsttime(sender, user, request, **kwargs):
    p = request.user.profile
    if not p.has_logged_in and p.email:
      # Send mail with some first-time information
      template = get_template('emails/welcome_information.html')

      data = Context({
        'name': p.name(),
        'protocol': 'https' if request.is_secure() else 'http',
        'domain': get_current_site(request).domain
      })
    
      message = template.render(data)
    
      from_email = settings.DEFAULT_FROM_EMAIL
    
      to_emails = [ p.email ]
      send_mail("Welkom!", message, from_email, to_emails, html_message=message)

      # Set to True
      p.has_logged_in = True
      p.save()

  user_logged_in.connect(check_firsttime, dispatch_uid="check_firsttime26112016")

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

  def is_favorite_for(self, profile):
    return self.favorited_by.filter(owner=profile).exists()

  def __str__(self):
    return "Profiel van %s" % self.name()

  def teamleader_of(self, team):
    # Check if user of users family is teamleader of this timetable's team
    return self.team_membership.filter(team=team, profile=self, is_admin=True).exists() or \
           self.family.team_membership.filter(team=team, family=self.family, is_admin=True).exists()

  def age(self):
    today = datetime.today().date()
    years = today.year - self.birthday.year
    is_before_birthday = (today.month, today.day) < (self.birthday.month, self.birthday.day)
    return years - int(is_before_birthday)

def family_pic(fam, filename):
  _, ext = os.path.splitext(filename)

  return 'families/%s%s' % (fam.pk, ext)

class Family(models.Model):

  lastname    = models.CharField(max_length=255)
  photo       = models.FileField(upload_to=family_pic, null=True, blank=True) #Todo: specify upload dir
  address     = models.OneToOneField(Address, null=True, blank=True, related_name="family")

  class Meta:
    ordering = ('lastname',)

  def __str__(self):
    return self.name_initials()

  def dads(self):
    return self.members.filter(role_in_family='DAD').order_by('birthday')

  def mums(self):
    return self.members.filter(role_in_family='MUM').order_by('birthday')

  def kids(self):
    return self.members.filter(role_in_family='KID').order_by('birthday')

  def name_initials(self):
    initials = ""

    for d in list(chain(self.dads(), self.mums())):
      if len(initials):
        initials += ", "
      initials += d.initials

    if len(initials) > 0:
      initials = " (%s)" % initials

    return "Familie %s%s" % (self.lastname, initials)

  def members_sorted(self):
    return list(chain(self.dads(), self.mums(), self.kids()))

  def size(self):
    return self.members.all().count()

  def delete(self, *args, **kwargs):
    # remove all ruilrequests
    for m in self.members.all():
      RuilRequest.objects.filter(profile=m).delete()

    super().delete(*args, **kwargs)

class Favorites(models.Model):

  owner       = models.ForeignKey(Profile, related_name="favorites")
  favorite    = models.ForeignKey(Profile, related_name="favorited_by")
