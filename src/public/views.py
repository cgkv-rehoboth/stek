from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.conf.urls import patterns, include, url
from django.template import RequestContext, loader
from django.views.generic import RedirectView
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta

from agenda.models import *
from public.models import *
from datetime import datetime
from cgkv.sitemaps import StaticViewSitemap
from fiber.models import Page, ContentItem


# Default function to render a specific Fiber page for a named route 'url'
# Returns the rendered page
def renderFiberPage(request, url):
  # Get CMS page from Fiber
  fiber_page = get_object_or_404(Page, url__exact=('"%s"' % (url)))

  # Get custom template, otherwise fall back to default (as provided in cgkv/settings.py)
  if fiber_page.metadata.get('static_fallback_page'):
    # Create custom fallback page
    template = fiber_page.metadata.get('static_fallback_page')
  elif fiber_page.template_name:
    template = fiber_page.template_name
  else:
    template = settings.FIBER_DEFAULT_TEMPLATE

  # Return the rendered template
  return render(request, template, {
    'fiber_page': fiber_page,
  })

def index(request):
  # Get CMS page from Fiber
  fiber_page = get_object_or_404(Page, url__exact='"index"')

  # Get custom template, otherwise fall back to default (as provided in cgkv/settings.py)
  if fiber_page.metadata.get('static_fallback_page'):
    # Create custom fallback page
    template = fiber_page.metadata.get('static_fallback_page')
  elif fiber_page.template_name:
    template = fiber_page.template_name
  else:
    # Get custom hardcoded template
    template = "public_index.html"

  # check if sunday
  now = datetime.now()
  listen_live = now.strftime('%w') == 0

  return render(request, template, {
    'fiber_page': fiber_page,
    'jaarthemas': fiber_page.page_content_items.filter(block_name='jaarthema_content').order_by('-sort'),
    'listen_live': listen_live,
    'recaptcha_publickey': settings.RECAPTCHA_PUBLIC_KEY,
  })

def kerktijden(request):
  # Render CMS page from Fiber
  return renderFiberPage(request, 'kerktijden')

def kindercreche(request):
  # Render CMS page from Fiber
  return renderFiberPage(request, 'kindercreche')

def orgel(request):
  # Render CMS page from Fiber
  return renderFiberPage(request, 'orgel')

def anbi(request):
  # Render CMS page from Fiber
  return renderFiberPage(request, 'anbi')

def robots(request):
  return render(request, 'robots.txt', {})


def diensten(request):
  # set default date to next sunday without a service
  # Get last sunday service
  last = Service.objects.filter(startdatetime__week_day=1).order_by('-startdatetime').first()

  # Add one week
  if last:
    startdatetime = last.startdatetime + timedelta(weeks=1)
  else:
    # Get next upcoming sunday
    today = datetime.today().date()
    startdatetime = today + timedelta(days=-today.weekday()-1, weeks=1)

  return render(request, 'list.html', {
    'startdatetime': startdatetime,
  })

urls = [
  url(r'^kerktijden$', RedirectView.as_view(url='kerktijden/', permanent=True)),
  url(r'^kerktijden/$', kerktijden, name='kerktijden'),

  url(r'^diensten/$', diensten, name='diensten'),

  url(r'^orgel$', RedirectView.as_view(url='orgel/', permanent=True)),
  url(r'^orgel/$', orgel, name='orgel'),

  url(r'^anbi$', RedirectView.as_view(url='anbi/', permanent=True)),
  url(r'^anbi/$', anbi, name='anbi'),

  url(r'^kindercreche$', RedirectView.as_view(url='kindercreche/', permanent=True)),
  url(r'^kindercreche/$', kindercreche, name='kindercreche'),

  url(r'^robots\.txt$', robots, name='robots'),

  # Everything else, look if Fiber can catch those (it's for custom pages from Fiber)
  url(r'^$', index, name='index')
]
