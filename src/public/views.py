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

urls = [
  url(r'^$', index)
]
