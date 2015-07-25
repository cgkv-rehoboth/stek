from django.contrib import admin
from .models import *

admin.site.register(Timetable)
admin.site.register(Event)
admin.site.register(Slide)
admin.site.register(Service)
admin.site.register(TimetableDuty)
admin.site.register(Address)
admin.site.register(Profile)
admin.site.register(FamilyMember)


# Create custom form for Family
class FamilyMemberInline(admin.TabularInline):
  model = FamilyMember
  extra = 0

class FamilyAdmin(admin.ModelAdmin):
  inlines = [FamilyMemberInline]

admin.site.register(Family, FamilyAdmin)
