from django.contrib import admin
from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.conf.urls import url

from .models import *


# Create custom display for Slide
class SlideAdmin(admin.ModelAdmin):
  list_display = ['title', 'order', 'slide_actions', 'live', 'showtext', 'description']
  ordering = ['order', 'title', 'live']
  search_fields = ['title', 'description', 'image']


  # Customize selection deletion to use the right delete function

  actions = ['delete_selected']

  def delete_selected(self, request, obj):
    for o in obj.all():
      o.delete()

  delete_selected.short_description = "Verwijder geselecteerde"


  # Custom default values for the form fields

  def formfield_for_dbfield(self, db_field, **kwargs):
    field = super(SlideAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    if db_field.name == 'order':
      # Increase the order
      last = Slide.objects.all().order_by('-order').first()

      if last:
        field.initial = last.order + 1
      else:
        field.initial = 1

    elif db_field.name == 'owner':
      # Set default owner
      field.initial = kwargs.get('request', None).user.profile.pk

    return field


  # Add up/down buttons for ordering

  # Add css files for the icons
  class Media:
    css = {
      'all': ('css/lib/font-awesome.min.css',)
    }

  def move_up(self, request, slide_pk, *args, **kwargs):
    Slide.objects.get(pk=slide_pk).move('UP')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

  def move_down(self, request, slide_pk, *args, **kwargs):
    Slide.objects.get(pk=slide_pk).move('DOWN')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

  # Add the URLs for the functions to the URLs of the admin page
  def get_urls(self):
    urls = super().get_urls()
    custom_urls = [
      url(
        r'^(?P<slide_pk>.+)/move/up/$',
        self.admin_site.admin_view(self.move_up),
        name='slide-move-up',
      ),
      url(
        r'^(?P<slide_pk>.+)/move/down/$',
        self.admin_site.admin_view(self.move_down),
        name='slide-move-down',
      ),
    ]
    return custom_urls + urls

  # Create buttons
  def slide_actions(self, obj):
    if obj.order < 2:
      if obj.order is Slide.objects.order_by('-order')[0].order:
        return format_html(
          '<i class="fa fa-arrow-circle-o-up fa-lg" style="color: #eee"></i>&nbsp;'
          '<i class="fa fa-arrow-circle-o-down fa-lg" style="color: #eee"></i>',
        )
      else:
        return format_html(
          '<i class="fa fa-arrow-circle-o-up fa-lg" style="color: #eee"></i>&nbsp;'
          '<a href="{}"><i class="fa fa-arrow-circle-o-down fa-lg"></i></a>',
          reverse('admin:slide-move-down', args=[obj.pk]),
      )
    elif obj.order is Slide.objects.order_by('-order')[0].order:
      return format_html(
        '<a href="{}"><i class="fa fa-arrow-circle-o-up fa-lg"></i></a>&nbsp;'
        '<i class="fa fa-arrow-circle-o-down fa-lg" style="color: #eee"></i>',
        reverse('admin:slide-move-up', args=[obj.pk]),
      )
    else:
      return format_html(
        '<a href="{}"><i class="fa fa-arrow-circle-o-up fa-lg"></i></a>&nbsp;'
        '<a href="{}"><i class="fa fa-arrow-circle-o-down fa-lg"></i></a>',
        reverse('admin:slide-move-up', args=[obj.pk]),
        reverse('admin:slide-move-down', args=[obj.pk]),
      )

  slide_actions.short_description = 'Actions'
  slide_actions.allow_tags = True

admin.site.register(Slide, SlideAdmin)
