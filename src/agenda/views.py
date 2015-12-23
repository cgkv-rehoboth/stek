from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django.contrib.auth.forms import AuthenticationForm
from django import http
import datetime

from .models import *

@login_required
def timetables(request):

  mytables = Timetable.objects.filter(team__members__pk=request.user.pk).exclude(team__isnull=True)
  notmytables = Timetable.objects.exclude(team__members__pk=request.user.pk).exclude(team__isnull=True)

  table_id = 0
  if mytables.exists():
    table_id = mytables[0].pk
  if request.GET and request.GET['table']:
    table_id = int(request.GET['table'])

  duties = TimetableDuty.objects.filter(timetable=table_id, event__startdatetime__gte=datetime.date.today()).order_by("event__startdatetime", "event__enddatetime")

  return render(request, 'timetables.html', {
    'table_id': table_id,
    'mytables': mytables,
    'notmytables': notmytables,
    'duties': duties
  })

urls = [
  url(r'^roosters$', timetables),
]
