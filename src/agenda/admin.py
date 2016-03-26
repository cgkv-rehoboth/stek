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

admin.site.register(Timetable, TimetableAdmin)

# Create custom display for TimetableDuty
class TimetableDutyAdmin(admin.ModelAdmin):
  list_display = ['responsible', 'event', 'timetable', 'comments']

admin.site.register(TimetableDuty, TimetableDutyAdmin)

# Create custom display for RuilRequest
class RuilRequestAdmin(admin.ModelAdmin):
  list_display = ['timetableduty', 'user', 'comments']

admin.site.register(RuilRequest, RuilRequestAdmin)

# Create custom display for Event
class EventAdmin(admin.ModelAdmin):
  list_display = ['title', 'startdatetime', 'enddatetime', 'timetable', 'description']

admin.site.register(Event, EventAdmin)

# Create custom display for Service
class ServiceAdmin(admin.ModelAdmin):
  list_display = ['title',  'minister', 'theme', 'startdatetime', 'enddatetime', 'description', 'comments']

admin.site.register(Service, ServiceAdmin)

# Team stuff
class TeamMemberAdmin(admin.ModelAdmin):
  list_display = ['user', 'team', 'role']

admin.site.register(TeamMember, TeamMemberAdmin)

# Create custom display for Team
class TeamMemberInline(admin.TabularInline):
  model = TeamMember
  extra = 0

class TeamAdmin(admin.ModelAdmin):
  inlines = [TeamMemberInline]
  list_display = ['name', 'leader', 'email', 'size']

admin.site.register(Team, TeamAdmin)
