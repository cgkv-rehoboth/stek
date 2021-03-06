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


class TimestampedModel(models.Model):

  class Meta:
    abstract = True

  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)


class Wijk(models.Model):

  id = models.IntegerField(primary_key=True)
  naam = models.CharField(max_length=255)

  class Meta:
    ordering = ('id',)

  def __str__(self):
    return "%s (%s)" % (self.naam, self.id)


class Address(TimestampedModel, models.Model):

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
  name = ''.join(e for e in unidecode(profile.name()) if e.isalnum())

  return 'profiles/%s_%s%s' % (profile.pk, name, ext)


class Profile(TimestampedModel, models.Model):

  user        = models.OneToOneField(User, null=True, blank=True, related_name="profile")
  address     = models.ForeignKey(Address, null=True, blank=True, related_name="profile")
  phone       = models.CharField(max_length=15, blank=True)
  first_name  = models.CharField(max_length=255, blank=True)
  initials    = models.CharField(max_length=64, blank=True, null=True, default="")
  last_name   = models.CharField(max_length=255, blank=True)
  prefix      = models.CharField(max_length=64, blank=True, null=True, default="")
  email       = models.CharField(max_length=255, blank=True, null=True)
  birthday    = models.DateField(null=True)
  photo       = models.ImageField(upload_to=user_profile_pic, null=True, blank=True)
  family      = models.ForeignKey("Family", null=True, related_name='members')
  has_logged_in  = models.NullBooleanField(null=True, default=False)

  # Extra
  voornamen   = models.CharField(max_length=255, null=True, blank=True, default="")
  geslacht    = models.CharField(max_length=15, null=True, blank=True, default="")
  soortlid    = models.CharField(max_length=15, null=True, blank=True, default="")
  burgerstaat = models.CharField(max_length=15, null=True, blank=True, default="")
  doopdatum   = models.DateField(null=True, blank=True)
  belijdenisdatum  = models.DateField(null=True, blank=True)
  huwdatum    = models.DateField(null=True, blank=True)
  overlijdensdatum = models.DateField(null=True, blank=True)
  lidnr       = models.IntegerField(null=True, blank=True)
  gvolgorde   = models.IntegerField(null=True, blank=True)
  titel       = models.CharField(max_length=15, null=True, blank=True, default="")
  is_active   = models.NullBooleanField(null=True, default=True)

  class Meta:
    unique_together = (('first_name', 'initials', 'last_name', 'prefix', 'birthday', 'lidnr'), )

  def delete(self, *args, **kwargs):
    # remove all dependencies
    RuilRequest.objects.filter(profile=self).delete()

    # Delete photo file
    self.photo.delete()

    super().delete(*args, **kwargs)

  def check_firsttime(sender, user, request, **kwargs):
    try:
      p = request.user.profile
    except Profile.DoesNotExist:
      print('User has no profile')
      return

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
      # Convert picture
      p = Image.open(self.photo).convert('RGB')

      # Preferred output image size (in pixels)
      prefsize = 400, 400

      ## Choose a option to save the profile picture
      # 1) Scale to max width and height
      #p = p.thumbnail(prefsize,Image.ANTIALIAS)

      # 2) Scale to max width or height
      #if p.size[0]>p.size[1]:
      #  size = prefsize[0], round(prefsize[1]*p.size[1]/p.size[0])
      #else:
      #  size = round(prefsize[0]*p.size[0]/p.size[1]), prefsize[1]
      #p = p.resize(size, Image.ANTIALIAS)

      # 3) Cropscale image to max width and height
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
    if self.address or not self.is_active:
      return self.address
    else:
      return self.family.address

  def name(self):
    if self.is_active:
      return "%s %s" % (self.first_name, self.last_namef())
    else:
      return "Verwijderd profiel"

  def namei(self):
    if self.is_active:
      return "%s %s" % (self.initials, self.last_namef())
    else:
      return "Verwijderd profiel"

  def first_namei(self):
    if self.is_active:
      return "%s, %s" % (self.first_name, self.initials)
    else:
      return "Verwijderd profiel"

  def last_namef(self):
    if self.is_active:
      if self.prefix == "":
        return self.last_name
      else:
        return "%s %s" % (self.prefix, self.last_name)
    else:
      return "Verwijderd profiel"

  def last_namep(self):
    if self.is_active:
      if self.prefix == "":
        return self.last_name
      else:
        return "%s, %s" % (self.last_name, self.prefix)
    else:
      return "Verwijderd profiel"

  def is_favorite_for(self, profile):
    return self.favorited_by.filter(owner=profile).exists()

  def __str__(self):
    if self.is_active:
      return "Profiel van %s" % self.name()
    else:
      return "Verwijderd profiel"

  def teamleader_of(self, team):
    # Check if user of users family is teamleader of this timetable's team
    return self.team_membership.filter(team=team, profile=self, is_admin=True).exists() or \
           self.family.team_membership.filter(team=team, family=self.family, is_admin=True).exists()

  def age(self):
    today = datetime.today().date()
    years = today.year - self.birthday.year
    is_before_birthday = (today.month, today.day) < (self.birthday.month, self.birthday.day)
    return years - int(is_before_birthday)

  def sex(self):
    if self.geslacht == "V" or self.geslacht == "Vrouw":
      return "V"
    elif self.geslacht == "M" or self.geslacht == "Man":
      return "M"
    else:
      return "O"


def family_pic(fam, filename):
  _, ext = os.path.splitext(filename)

  # Remove all harmfull chars
  name = ''.join(e for e in unidecode(fam.lastnamep()) if e.isalnum())

  return 'families/%s_%s%s' % (fam.pk, name, ext)


def family_pic_thumb(fam, filename):
  _, ext = os.path.splitext(filename)

  # Remove all harmfull chars
  name = ''.join(e for e in unidecode(fam.lastnamep()) if e.isalnum())

  return 'families/thumbnails/%s_%s%s' % (fam.pk, name, ext)


class Family(TimestampedModel, models.Model):

  lastname    = models.CharField(max_length=255)
  photo       = models.FileField(upload_to=family_pic, null=True, blank=True)
  thumbnail   = models.FileField(upload_to=family_pic_thumb, null=True, blank=True)
  address     = models.OneToOneField(Address, null=True, blank=True, related_name="family")

  # Extra
  prefix      = models.CharField(max_length=64, blank=True, null=True, default="")
  aanhef      = models.CharField(max_length=15, null=True, blank=True, default="")
  gezinsnr    = models.IntegerField(null=True, blank=True)
  is_active   = models.NullBooleanField(null=True, default=True)

  class Meta:
    unique_together = (('lastname', 'prefix', 'gezinsnr'), )
    ordering = ('lastname', 'prefix')

  def __str__(self):
    return "Familie %s" % self.name_initials()

  def email(self):
    mem = self.members_sorted().exclude(email=None).exclude(email='').first()
    if mem:
      return mem.email
    else:
      return ''

  def householder(self):
    # Gezinshoofd
    return self.members.filter(gvolgorde=1).order_by('birthday')

  def partner(self):
    # Partner van gezinshoofd
    return self.members.filter(gvolgorde=2).order_by('birthday')

  def kids(self):
    # Kinderen
    return self.members.exclude(gvolgorde__in=[1, 2]).order_by('birthday')

  def lastnamef(self):
    if self.prefix == "":
      return self.lastname
    else:
      return "%s %s" % (self.prefix, self.lastname)

  def lastnamep(self):
    if self.prefix == "":
      return self.lastname
    else:
      return "%s, %s" % (self.lastname, self.prefix)

  def name_initials(self):
    initials = ""

    for d in self.members.filter(gvolgorde__in=[1, 2]):
      if len(initials):
        initials += ", "
      initials += d.initials

    if len(initials) > 0:
      initials = " (%s)" % initials

    return "%s%s" % (self.lastnamep(), initials)

  def members_sorted(self):
    return self.members.order_by('gvolgorde', 'birthday')

  def size(self):
    return self.members.all().count()

  def delete(self, *args, **kwargs):
    # remove all ruilrequests
    for m in self.members.all():
      RuilRequest.objects.filter(profile=m).delete()

    # Delete photo files
    self.photo.delete()
    self.thumbnail.delete()

    super().delete(*args, **kwargs)

  def save(self, *args, **kwargs):
    # Check if a new photo/thumnail has been submitted
    if args and args[0] and ((args[0] == 'photo' and self.photo) or (args[0] == 'thumbnail' and self.thumbnail)):
      # Convert picture
      if args[0] == 'thumbnail' and self.thumbnail:
        p = Image.open(self.thumbnail).convert('RGB')
      else:
        p = Image.open(self.photo).convert('RGB')

      ## Thumbnail photo
      # Preferred output image size (in pixels)
      prefsize = 300, 300

      # 2) Scale to max width or height
      if p.size[0]>p.size[1]:
        size = prefsize[0], round(prefsize[1]*p.size[1]/p.size[0])
      else:
        size = round(prefsize[0]*p.size[0]/p.size[1]), prefsize[1]
      p_thumbnail = p.resize(size, Image.ANTIALIAS)

      # Save
      output_thumbnail = BytesIO()
      p_thumbnail.save(output_thumbnail, format='JPEG', quality=90, optimize=True)
      output_thumbnail.seek(0, os.SEEK_END)
      self.thumbnail = InMemoryUploadedFile(output_thumbnail, 'ImageField', "%s.jpg" % self.photo.name, 'image/jpeg', output_thumbnail.tell(), None)

      ## Full photo
      if args[0] == 'photo':
        # Preferred output image size (in pixels)
        prefsize = 800, 800

        # 2) Scale to max width or height
        if p.size[0] > p.size[1]:
          size = prefsize[0], round(prefsize[1] * p.size[1] / p.size[0])
        else:
          size = round(prefsize[0] * p.size[0] / p.size[1]), prefsize[1]
        p_full = p.resize(size, Image.ANTIALIAS)

        # Save
        output_full = BytesIO()
        p_full.save(output_full, format='JPEG', quality=90, optimize=True)
        output_full.seek(0, os.SEEK_END)
        self.photo = InMemoryUploadedFile(output_full, 'ImageField', "%s.jpg" % self.photo.name, 'image/jpeg',
                                          output_full.tell(), None)

      # Reset arguments
      args = {}

    super().save(*args, **kwargs)


class Favorites(models.Model):

  owner       = models.ForeignKey(Profile, related_name="favorites")
  favorite    = models.ForeignKey(Profile, related_name="favorited_by")

  def __str__(self):
    return "%s <3 %s" % (self.owner.name(), self.favorite.name())
