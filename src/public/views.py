from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django import forms
from django.core.mail import send_mail
from django.conf import settings

from agenda.models import *
from datetime import datetime

def index(request):
  # check if sunday
  now = datetime.now()
  listen_live = now.strftime('%w') == 0

  return render(request, 'index.html', {
    'listen_live': listen_live,
    'services': Service.objects.all(),
    'recaptcha_publickey': settings.RECAPTCHA_PUBLIC_KEY
  })

def kerktijden(request):
  return render(request, 'kerktijden.html', {})

def kindercreche(request):
  return render(request, 'kerktijden.html', {})

def orgel(request):
  return render(request, 'orgel.html', {})

def anbi(request):
  return render(request, 'anbi.html', {})

urls = [
  url(r'^kerktijden/$', kerktijden, name='kerktijden'),
  url(r'^orgel/$', orgel, name='orgel'),
  url(r'^anbi/$', anbi, name='anbi'),
  url(r'^kindercreche/$', kindercreche, name='kindercreche'),
  url(r'^$', index)
]
