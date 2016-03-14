from django.shortcuts import render
from django.conf.urls import patterns, include, url

from agenda.models import *
from datetime import datetime

def index(request):
  # check if sunday
  now = datetime.now()
  listen_live = now.strftime('%w') == 0

  return render(request, 'index.html', {
    'listen_live': listen_live,
    'services': Service.objects.all()
  })

urls = [
  url(r'^$', index),
]
