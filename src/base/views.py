from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django.contrib.auth.forms import AuthenticationForm
from django import http

from .models import *

def timetables(request):

  doodies = TimetableDuty.objects.all()
  by_table = {}
  for doodie in doodies:
    by_table[doodie.timetable] = by_table.get(doodie.timetable, []) + [doodie]

  return render(request, 'timetables.html', {
    'doodies': by_table
  })

def index(request):
  return render(request, 'index.html', {
    'services': Service.objects.all()
  })

def login(request):
  if request.method == 'POST':
    form = AuthenticationForm(data=request.POST)
    submitted = True
  else:
    form = AuthenticationForm()
    submitted = False

  if submitted and form.is_valid():
    return http.HttpResponseRedirect('/')
  else:
    return render(request, 'login.html', { 'form': AuthenticationForm() })

urls = [
  url(r'^$', index),
  url(r'^login$', login, name='login'),

  url(r'^roosters$', timetables),
]
