from django.shortcuts import render
from django.conf.urls import patterns, include, url

from agenda.models import *

def index(request):
  return render(request, 'index.html', {
    'services': Service.objects.all()
  })

urls = [
  url(r'^$', index),
]
