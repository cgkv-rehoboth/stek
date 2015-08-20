from django.contrib import admin
from .models import *

admin.site.register(Timetable)
admin.site.register(Event)
admin.site.register(Slide)
admin.site.register(Service)
admin.site.register(TimetableDuty)
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

# Create custom display for User
class ProfileInline(admin.StackedInline):
  model = Profile
  extra = 1
  max_num = 1

class UserAdmin(admin.ModelAdmin):
  fieldsets = [
    ('User',   {'fields': ['username', 'password', 'first_name', 'last_name', 'email']}),
    ('Extra',  {'fields': ['groups', ], 'classes': ['collapse']}),
  ]
  inlines = [ProfileInline, FamilyMemberInline]
  list_display = ['last_name', 'first_name', 'username', 'email', 'is_active', 'last_login']
  list_display_links = ['username']
  list_filter = ['is_active']
  ordering = ['last_name', 'first_name', 'username']
  search_fields = ['first_name', 'last_name']

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Create custom display for Profile
class ProfileAdmin(admin.ModelAdmin):
  list_display = ['user', 'address', 'phone', 'birthday']

admin.site.register(Profile, ProfileAdmin)