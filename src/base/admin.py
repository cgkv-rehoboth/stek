from django.contrib import admin
from .models import *

admin.site.register(Timetable)
admin.site.register(Event)
admin.site.register(Slide)
admin.site.register(Service)
admin.site.register(TimetableDuty)
admin.site.register(Profile)
admin.site.register(FamilyMember)

# Create custom display for Address
class AddressAdmin(admin.ModelAdmin):
  list_display = ['street', 'zip', 'city', 'country']

admin.site.register(Address, AddressAdmin)

# Create custom display for Family
class FamilyMemberInline(admin.TabularInline):
  model = FamilyMember
  extra = 0

class FamilyAdmin(admin.ModelAdmin):
  inlines = [FamilyMemberInline]
  list_display = ['lastname', 'size']

admin.site.register(Family, FamilyAdmin)
