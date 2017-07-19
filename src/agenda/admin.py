from django.contrib import admin
from .models import *
from datetime import datetime

# Create custom display for TimeTable
class TimetableDutyInline(admin.TabularInline):
  model = TimetableDuty
  extra = 0

  def get_queryset(self, request):
    return TimetableDuty.objects.filter(
      event__startdatetime__gte=datetime.now().replace(hour=0, minute=0, second=0))

class TimetableAdmin(admin.ModelAdmin):
  inlines = [TimetableDutyInline]
  list_display = ['title', 'team', 'description']

  # Custom default values for the form fields
  def formfield_for_dbfield(self, db_field, **kwargs):
    field = super(TimetableAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    if db_field.name == 'owner':
      # Set default owner
      field.initial = kwargs.get('request', None).user.profile.pk

    return field

admin.site.register(Timetable, TimetableAdmin)

# Create custom display for TimetableDuty
class TimetableDutyAdmin(admin.ModelAdmin):
  list_display = ['resp_name', 'event', 'timetable', 'comments']

admin.site.register(TimetableDuty, TimetableDutyAdmin)

# Create custom display for RuilRequest
class RuilRequestAdmin(admin.ModelAdmin):
  list_display = ['timetableduty', 'profile', 'comments']

admin.site.register(RuilRequest, RuilRequestAdmin)

# Create custom display for Event
class EventAdmin(admin.ModelAdmin):
  list_display = ['title', 'startdatetime', 'enddatetime', 'timetable', 'description']

  # Custom default values for the form fields
  def formfield_for_dbfield(self, db_field, **kwargs):
    field = super(EventAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    if db_field.name == 'owner':
      # Set default owner
      field.initial = kwargs.get('request', None).user.profile.pk

    return field

admin.site.register(Event, EventAdmin)

# Create custom display for Service
class ServiceAdmin(admin.ModelAdmin):
  list_display = ['title',  'minister', 'theme', 'startdatetime', 'enddatetime', 'description', 'comments']

admin.site.register(Service, ServiceAdmin)

class EventFileAdmin(admin.ModelAdmin):
  list_display = ['title', 'event', 'file', 'filesize', 'is_public', 'modified_date']

  ordering = ('-modified_date', '-event', 'title')

  # Custom default values for the form fields
  def formfield_for_dbfield(self, db_field, **kwargs):
    field = super(EventFileAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    if db_field.name == 'owner':
      # Set default owner
      field.initial = kwargs.get('request', None).user.profile.pk

    return field

admin.site.register(EventFile, EventFileAdmin)

# Create custom display for TimetableDuty
class TeamMemberRoleAdmin(admin.ModelAdmin):
  list_display = ['name', 'short_name', 'is_active']
  ordering = ['-is_active', 'name']

admin.site.register(TeamMemberRole, TeamMemberRoleAdmin)

# Team stuff
class TeamMemberAdmin(admin.ModelAdmin):
  list_display = ['name', 'team', 'role', 'is_admin', 'get_mail']

admin.site.register(TeamMember, TeamMemberAdmin)

# Create custom display for Team
class TeamMemberInline(admin.TabularInline):
  model = TeamMember
  extra = 0

class TeamAdmin(admin.ModelAdmin):
  inlines = [TeamMemberInline]
  list_display = ['name', 'get_leader_names', 'email', 'size']

  def get_leader_names(self, obj):
    # Return a string with all the names of the leaders (profile and families)
    return ", ".join(
      [ (m.profile.namei() if m.profile else str(m.family)) for m in obj.leaders() ]
    )

admin.site.register(Team, TeamAdmin)
