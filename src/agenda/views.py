from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django.contrib.auth.forms import AuthenticationForm
from django import http
import datetime

from .models import *

@login_required
def timetables(request):
  table_id = 1
  if request.GET and request.GET['table']:
    table_id = int(request.GET['table'])

  duties = TimetableDuty.objects.filter(timetable=table_id, event__startdatetime__gte=datetime.date.today()).order_by("event__startdatetime", "event__enddatetime")

  mytables = Timetable.objects.filter(team__members__pk=request.user.pk).exclude(team__isnull=True)
  notmytables = Timetable.objects.exclude(team__members__pk=request.user.pk).exclude(team__isnull=True)

  return render(request, 'timetables.html', {
    'table_id': table_id,
    'mytables': mytables,
    'notmytables': notmytables,
    'duties': duties
  })

urls = [
  url(r'^roosters$', timetables),
]
