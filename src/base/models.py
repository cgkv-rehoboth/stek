from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from livefield.models import LiveModel
from django.db.models import Count

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

class Profile(models.Model):

  user        = models.OneToOneField(User, null=True, blank=True, related_name="profile")
  address     = models.ForeignKey(Address, null=True, blank=True)
  phone       = models.CharField(max_length=15, blank=True)
  birthday    = models.DateField()
  photo       = models.ImageField(upload_to='/') #Todo: specify upload dir

  def __str__(self):
    return "Profiel van %s" % (self.user.username)

class Family(models.Model):

  lastname    = models.CharField(max_length=255)
  members     = models.ManyToManyField(User, through="FamilyMember")
  photo       = models.ImageField(upload_to='/') #Todo: specify upload dir

  def __str__(self):
    # Get the head of the family (mainly the father of the family) ...
    head = self.members.filter(familymember__role='DAD').first()

    # ... otherwise the eldest
    if not head:
      head = self.members.all().order_by('profile__birthday').first()

    return "Familie %s, %s." % (self.lastname, head.first_name[:1])

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

  family      = models.ForeignKey(Family)
  user        = models.ForeignKey(User)
  role        = models.CharField(max_length=3, choices=ROLE_CHOICES, default=KID)

  def __str__(self):
    return "%s %s: %s" % (self.family.lastname, self.get_role_display(), self.user.username)