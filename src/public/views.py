from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django import forms
from django.core.mail import send_mail
from django.conf import settings

from agenda.models import *
from datetime import datetime
from cgkv.sitemaps import StaticViewSitemap

def index(request):
  # check if sunday
  now = datetime.now()
  listen_live = now.strftime('%w') == 0

  return render(request, 'index.html', {
    'listen_live': listen_live,
    'recaptcha_publickey': settings.RECAPTCHA_PUBLIC_KEY,
    'sitemaps': StaticViewSitemap.itemnames(StaticViewSitemap),
    #'jaarthema_publish_date': (datetime.now() > datetime.strptime('22-08-2016 00:00', '%d-%m-%Y %H:%M'))
  })

def kerktijden(request):
  return render(request, 'kerktijden.html', {
    'sitemaps': StaticViewSitemap.itemnames(StaticViewSitemap),
  })

def kindercreche(request):
  return render(request, 'kerktijden.html', {
    'sitemaps': StaticViewSitemap.itemnames(StaticViewSitemap),
  })

def orgel(request):
  return render(request, 'orgel.html', {
    'sitemaps': StaticViewSitemap.itemnames(StaticViewSitemap),
  })

def anbi(request):
  return render(request, 'anbi.html', {
    'sitemaps': StaticViewSitemap.itemnames(StaticViewSitemap),
  })

urls = [
  url(r'^kerktijden$', RedirectView.as_view(url='kerktijden/', permanent=True)),
  url(r'^kerktijden/$', kerktijden, name='kerktijden'),

  url(r'^orgel$', RedirectView.as_view(url='orgel/', permanent=True)),
  url(r'^orgel/$', orgel, name='orgel'),

  url(r'^anbi$', RedirectView.as_view(url='anbi/', permanent=True)),
  url(r'^anbi/$', anbi, name='anbi'),

  url(r'^kindercreche$', RedirectView.as_view(url='kindercreche/', permanent=True)),
  url(r'^kindercreche/$', kindercreche, name='kindercreche'),

  url(r'^$', index, name='index')
]
