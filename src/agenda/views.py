from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django.contrib.auth.forms import AuthenticationForm
from django import http
import datetime
from django.contrib import messages
from .models import *

@login_required
def timetables(request):
  # Check if someone triggerd the 'ruilen'-form
  if 'modal-duty-pk' in request.POST:
    # Get the duty in question
    duty = TimetableDuty.objects.filter(pk=request.POST['modal-duty-pk'])[:1].get()

    # Generate the message for the leaders of the team
    message = "Hello!\n\n" + request.user.username + " just announced that (s)he can't do the shift of the event '" + str(duty.event) + "'.\n"

    if request.POST['comments'] != "":
      message += request.user.username + " added this note: \n" + request.POST['comments']

    # Get the email of the leaders
    recipients = []

    for v in TeamMember.objects.filter(team_id=duty.timetable.team.pk, role="LEI"):
      recipients.append(v.user.email)

    #send_mail("Ruilverzoek " + duty.event.title, message, "noreply@cgkvwoerden.nl", recipients)

    # Set feedback/status message to inform the user
    messages.success(request, 'De teamleiding is op de hoogte gebracht van je verzoek!')

    # Redirect to the same page, to prevent re-submitting the form on page-reload
    return HttpResponseRedirect('/roosters?table=' + str(duty.timetable.pk))


  # Get all the tables linked to the team(s) the user is in
  mytables = Timetable.objects.filter(team__members__pk=request.user.pk).exclude(team__isnull=True)
  # Get all the other tables that are not really relevant to the user
  notmytables = Timetable.objects.exclude(team__members__pk=request.user.pk).exclude(team__isnull=True)

  # Start with no table id
  table_id = 0

  # Get the first-to-see table id
  if mytables.exists():
    table_id = mytables[0].pk

  # Get the requested table id
  if request.GET and request.GET['table']:
    table_id = int(request.GET['table'])

  # Get all the duties from the specific table
  duties = TimetableDuty.objects.filter(timetable=table_id, event__startdatetime__gte=datetime.date.today()).order_by("event__startdatetime", "event__enddatetime")

  # Render that stuff!
  return render(request, 'timetables.html', {
    'table_id': table_id,
    'mytables': mytables,
    'notmytables': notmytables,
    'duties': duties,

    'events': Event.objects.filter(startdatetime__gte=datetime.date.today()).order_by('startdatetime'),#.exclude(duties__in=duties),
    'users': User.objects.filter(team_membership__team__timetables=table_id)
  })

urls = [
  url(r'^roosters$', timetables),
]
