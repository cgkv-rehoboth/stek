from django.contrib import admin
from .models import *

admin.site.register(Slide)
admin.site.register(Favorites)

# Create custom display for Address
class AddressAdmin(admin.ModelAdmin):
  list_display = ['street', 'zip', 'city', 'country']

admin.site.register(Address, AddressAdmin)

class FamilyAdmin(admin.ModelAdmin):
  list_display = ['lastname', 'size']

admin.site.register(Family, FamilyAdmin)

# Create custom display for User
class ProfileInline(admin.StackedInline):
  model = Profile
  extra = 1
  max_num = 1

class UserAdmin(admin.ModelAdmin):
  fieldsets = [
    ('User',   {'fields': ['username', 'first_name', 'last_name', 'email']}),
    ('Extra',  {'fields': ['groups', ], 'classes': ['collapse']}),
  ]
  inlines = [ProfileInline]
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
