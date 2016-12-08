from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from livefield.models import LiveModel
from django.db.models import Count
from django.core.urlresolvers import reverse
import os

# Import models of base app
from base.models import Profile, Family

class ActiveManager(models.Manager):
  # Get online the active ones when calling objects.active()
  def active(self):
    return super(ActiveManager, self).get_queryset().filter(is_active=True)

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

  def delete(self, *args, **kwargs):
    # Delete ruilrequest belonging to this table
    self.duties.all().delete()

    super().delete(*args, **kwargs)

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
    #date = self.startdatetime.strftime("%d %B, %H:%M") # Wrong translation
    date = self.startdatetime.strftime("%d-%m-%Y, %H:%M")
    return "%s, op %su" % (self.title, date)

class TimetableDuty(models.Model):

  responsible = models.ForeignKey(Profile, related_name="duties", blank=True, null=True)
  responsible_family = models.ForeignKey(Family, related_name="duties", blank=True, null=True)
  event       = models.ForeignKey(Event, related_name="duties")
  timetable   = models.ForeignKey(Timetable, related_name="duties")
  comments    = models.TextField(blank=True, null=True)

  def __str__(self):
    if self.responsible:
      return "%s op %s door %s" % (self.event.title, self.event.startdatetime.strftime("%d-%m-%Y, %H:%M"), self.responsible.name())
    elif self.responsible_family:
      return "%s op %s door familie %s" % (self.event.title, self.event.startdatetime.strftime("%d-%m-%Y, %H:%M"), self.responsible_family.lastname)
    else:
      return "%s op %s door %s" % (self.event.title, self.event.startdatetime.strftime("%d-%m-%Y, %H:%M"), "niemand")

  def delete(self, *args, **kwargs):
    # Delete ruilrequest belonging to this duty
    self.ruilen.all().delete()

    super().delete(*args, **kwargs)

  def resp_name(self):
    if self.responsible:
      return self.responsible.name()
    elif self.responsible_family:
      return str(self.responsible_family)
    else:
      return "niemand"

class Service(Event):

  minister    = models.CharField(max_length=255)
  theme       = models.CharField(max_length=255, blank=True, default="")
  comments    = models.TextField(blank=True, null=True)

  def save(self, *args, **kwargs):
    if self.title == "": self.title = "Dienst"

    super(Service, self).save(*args, **kwargs)

  def url(self, *args, **kwargs):
    return reverse('services-single', kwargs={'id': self.pk})

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
    return self.teammembers.filter(is_admin=True)

class TeamMemberRole(models.Model):

  name            = models.CharField(max_length=255, unique=True)
  short_name      = models.CharField(max_length=4)
  is_active       = models.BooleanField(default=True)

  objects         = ActiveManager()

  def __str__(self):
    return self.name

  def delete(self, *args, **kwargs):
    # Delete teammembers
    self.teammembers.all().delete()

    super().delete(*args, **kwargs)

class TeamMember(models.Model):

  team        = models.ForeignKey(Team, related_name="teammembers")
  profile     = models.ForeignKey(Profile, related_name="team_membership", blank=True, null=True)
  family      = models.ForeignKey(Family, related_name="team_membership", blank=True, null=True)
  role        = models.ForeignKey(TeamMemberRole, related_name="teammembers", default=1)
  is_admin    = models.BooleanField(default=False)

  def __str__(self):
    return "%s %s" % (self.team.name, self.role)

  def name(self):
    if self.family:
      return "Famlie %s" % self.family.lastname
    else:
      return self.profile.name()

class RuilRequest(models.Model):

  timetableduty   = models.ForeignKey(TimetableDuty, related_name="ruilen")
  profile         = models.ForeignKey(Profile, related_name="ruilen")
  comments        = models.TextField(blank=True)

  class Meta:
    unique_together = (("timetableduty", "profile"),)

def eventfilepath(instance, filename):
  return 'eventfiles/%s' % (filename)

class EventFile(TimestampedModel, models.Model):

  title       = models.CharField(max_length=255)
  event       = models.ForeignKey(Event, related_name="files")
  file        = models.FileField(upload_to=eventfilepath)
  owner       = models.ForeignKey(Profile, related_name="files")
  is_public   = models.BooleanField(default=True)

  def filename(self):
    return "%s" % os.path.basename(self.file.path)

  def filesize(self):
    size = self.file.size

    if size == 1:
      return "%3.0f %s" % (size, 'byte')

    for unit in ['bytes','kB','MB','GB','TB','PB','EB','ZB']:
      if abs(size) < 1024.0:
        if unit is 'bytes':
          return "%3.0f %s" % (size, unit)
        else:
          return "%3.1f %s" % (size, unit)
      size /= 1024.0

    return "%.1f %s" % (size, 'YB')

  def type(self):
    ext = os.path.splitext(self.file.path)[1].replace('.', '')
    type = ''
    icons = [
      ('powerpoint', ['ppt', 'pptx', 'pps']),
      ('word', ['doc', 'docx', 'odt']),
      ('pdf', ['pdf']),
      ('image', ['jpg', 'jpeg', 'png', 'gif', 'svg']),
      ('excel', ['xls', 'xlsx', 'xlr']),
      ('text', ['txt', 'log']),
      ('audio', ['mp3', 'wav', '3ga', 'm4a', 'mpa', 'wma', 'mid']),
      ('video', ['mp4', 'wmv', 'avi', 'mov', 'flv', 'm4v', 'mpg', 'mpeg', '3gp']),
      ('zip', ['tgz', 'gz', 'zip', 'rar']),
      ('code', ['html', 'js', 'css', 'py', 'php', 'json', 'xml', 'rtf', 'tex', 'csv', 'vcf']),
    ]
    for i in icons:
      if ext in i[1]:
        type = i[0]
        continue

    return type


  def iconHTML(self):
    type = self.type()
    if type:
      type += '-'

    return '<i class="fa fa-file-%so" aria-hidden="true"></i>' % type


  def delete(self, *args, **kwargs):
    # Delete file
    self.file.delete()

    super().delete(*args, **kwargs)
