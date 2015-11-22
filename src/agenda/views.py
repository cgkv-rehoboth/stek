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

urls = [
  url(r'^roosters$', timetables),
]
