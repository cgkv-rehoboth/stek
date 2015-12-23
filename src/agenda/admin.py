from django.contrib import admin
from .models import *

admin.site.register(Timetable)
admin.site.register(TimetableDuty)
admin.site.register(Service)


# Create custom display for TimeTable
class TimetableDutyInline(admin.TabularInline):
  model = TimetableDuty
  extra = 0

class EventAdmin(admin.ModelAdmin):
  inlines = [TimetableDutyInline]

admin.site.register(Event, EventAdmin)

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
