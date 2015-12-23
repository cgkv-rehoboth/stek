from django.contrib import admin
from .models import *

admin.site.register(Service)


# Create custom display for TimeTable
class TimetableDutyInline(admin.TabularInline):
  model = TimetableDuty
  extra = 0

class TimetableAdmin(admin.ModelAdmin):
  inlines = [TimetableDutyInline]
  list_display = ['title', 'team', 'description']

admin.site.register(Timetable, TimetableAdmin)

# Create custom display for TimetableDuty
class TimetableDutyAdmin(admin.ModelAdmin):
  list_display = ['responsible', 'event', 'timetable', 'comments']

admin.site.register(TimetableDuty, TimetableDutyAdmin)

# Create custom display for Event
class EventAdmin(admin.ModelAdmin):
  list_display = ['title', 'startdatetime', 'enddatetime', 'timetable', 'repeatEveryMin', 'description']

  def repeatEveryMin(self, obj):
    return obj.repeatEvery
  repeatEveryMin.short_description = "RepeatEvery (minutes)"

admin.site.register(Event, EventAdmin)

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
