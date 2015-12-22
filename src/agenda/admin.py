from django.contrib import admin
from .models import *

admin.site.register(Timetable)
admin.site.register(Event)
admin.site.register(TimetableDuty)
admin.site.register(Service)


admin.site.register(TeamMember)


# Create custom display for Team
class TeamMemberInline(admin.TabularInline):
  model = TeamMember
  extra = 0

class TeamAdmin(admin.ModelAdmin):
  inlines = [TeamMemberInline]
  list_display = ['name', 'size']

admin.site.register(Team, TeamAdmin)
