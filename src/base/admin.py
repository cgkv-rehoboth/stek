from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

admin.site.register(Wijk)
admin.site.register(Favorites)

# Create custom display for Address
class AddressAdmin(admin.ModelAdmin):
  list_display = ['street', 'zip', 'city', 'country', 'occupant']

admin.site.register(Address, AddressAdmin)

class FamilyAdmin(admin.ModelAdmin):
  list_display = ['lastname', 'size']

  def save_model(self, request, obj, form, change):
    args = {}
    # Remove old photo
    if request.FILES.get('photo'):
      Family.objects.get(pk=obj.pk).photo.delete()
      Family.objects.get(pk=obj.pk).thumbnail.delete()
      args = 'photo'
    if request.FILES.get('thumbnail'):
      Family.objects.get(pk=obj.pk).thumbnail.delete()
      args = 'thumbnail'

    obj.save(args)

admin.site.register(Family, FamilyAdmin)

# Create custom display for User
class ProfileInline(admin.StackedInline):
  model = Profile
  extra = 0
  max_num = 1

class UserAdmin(BaseUserAdmin):
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
  list_display = ['name', 'address', 'phone', 'email', 'birthday', 'has_logged_in']
  ordering = ['last_name', 'first_name']
  search_fields = ['first_name', 'last_name']

admin.site.register(Profile, ProfileAdmin)
