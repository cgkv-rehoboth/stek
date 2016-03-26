from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf.urls import include, url
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime
from .models import *

"""
def form(request):
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

  send_mail("Ruilverzoek " + duty.event.title, message, "noreply@cgkvwoerden.nl", recipients)

  # Set feedback/status message to inform the user
  messages.success(request, 'De teamleiding is op de hoogte gebracht van je verzoek!')

  # Redirect to the same page, to prevent re-submitting the form on page-reload
  return HttpResponseRedirect('/roosters?table=' + str(duty.timetable.pk))
"""

@login_required
def add_event(request):
  return render(request, 'add_event.html', {})

@login_required
def timetables(request, id=None):

  # Get all the tables linked to the team(s) the user is in
  mytables = list(Timetable\
    .objects\
    .filter(team__members__pk=request.user.pk)\
    .exclude(team__isnull=True))

  # Get the first-to-see table id
  if id is None and len(mytables) > 0:
    id = mytables[0].pk

  # Get current table
  table = Timetable.objects.prefetch_related('team__members').filter(pk=id).first()

  duties = table.duties\
    .filter(event__startdatetime__gte=datetime.today().date())\
    .order_by("event__startdatetime", "event__enddatetime")


  # Connect each duty with a ruilRequest
  ruilrequests = RuilRequest.objects.all()
  for duty in duties:
    for ruil in ruilrequests:
      if(duty == ruil.timetableduty):
        if(ruil.user == request.user):
          # Current user has requested a 'ruilverzoek'
          duty.ruilrequest = 2
        else:
          # Other user has requested a 'ruilverzoek'
          duty.ruilrequest = 1
        break
      else:
        # No one has requested a 'ruilverzoek'
        duty.ruilrequest = 0

  # Get all the other tables
  # that are not really relevant to the user
  notmytables = list(Timetable\
    .objects\
    .exclude(team__members__pk=request.user.pk)\
    .exclude(team__isnull=True)\
    .exclude(pk=id))

  # Render that stuff!
  return render(request, 'timetables.html', {
    'current_table': table,
    'duties': duties,
    'mytables': mytables,
    'notmytables': notmytables
  })


@login_required
def timetableruilen(request, id):
  # Check if it is a legit 'ruil' request
  if(request.method == 'POST' and request.POST.get("modal-duty-pk") and TimetableDuty.objects.filter(pk=int(request.POST.get("modal-duty-pk"))).exists()):
    # Check if record already exitst
    record = RuilRequest.objects.filter(timetableduty_id=int(request.POST.get("modal-duty-pk")))
    if(record.exists()):
      record = record.first()
      # Check if the same user submitted
      if(record.user == request.user):
        # Delete record
        record.delete()
      else:
        # Update record with new user
        record.user = request.user
        record.comments = request.POST.get("comments", "")
        record.save()
    else:
      # Create record
      record = RuilRequest(timetableduty_id=int(request.POST.get("modal-duty-pk")), user=request.user, comments=request.POST.get("comments", ""))
      record.save()

      # Inform team leader
      template = get_template('email/ruilverzoek.txt')
      duty = TimetableDuty.objects.filter(pk=int(request.POST.get("modal-duty-pk"))).first()

      if request.POST.get("comments"):
        comments = "Met de volgende redenen: \n %s" % request.POST.get("comments", "")
      else:
        comments = "Er is geen reden gegeven."

      data = Context({
        'name': request.user.profile.name,
        'timetable': duty.timetable.title,
        'duty': duty,
        'comments': comments
      })
      message = template.render(data)

      # Todo: uncomment for real live action
      #send_mail("Ruilverzoek", message, 'noreply@domein.nl', duty.timetable.team.leader_email())

  # Redirect to timetable-detail page to prevent re-submitting and to show the changes
  return redirect('timetable-detail-page', id=id)


@login_required
def calendar(request):
  return render(request, 'calendar.html')

urls = [
  url(r'^roosters/ruilen/(?P<id>\d+)/$', timetableruilen, name='timetable-ruilen'),
  url(r'^roosters/(?P<id>\d+)/$', timetables, name='timetable-detail-page'),
  url(r'^roosters/$', timetables, name='timetable-list-page'),
  url(r'^kalender/$', calendar, name='calendar-page'),
  url(r'^kalendar/nieuw/$', add_event, name='add-event-page'),
]
