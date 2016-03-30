from django.contrib.auth.decorators import login_required
from django.views.decorators.http import *
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf.urls import include, url
from django.conf import settings
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime
from .models import *

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

  if table is not None: 
    duties = table.duties\
      .prefetch_related('ruilen')\
      .filter(event__startdatetime__gte=datetime.today().date())\
      .order_by("event__startdatetime", "event__enddatetime")
  else:
    duties = []

  ruilen = {}
  for duty in duties:
    for req in duty.ruilen.all():
      # sanity check
      # only a single request can pass this check
      # due to the uniqueness constraint on requests
      if req.user == duty.responsible:
        duty.ruilrequest = req

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
@require_POST
def timetable_undo_ruilen(request, id):
  req = RuilRequest.objects.prefetch_related('timetableduty__timetable').get(pk=id)

  # delete the request
  req.delete()

  return redirect('timetable-detail-page', id=req.timetableduty.timetable.pk)

@login_required
@require_POST
def timetable_ruilen(request, id):
  duty = TimetableDuty.objects.get(pk=id)

  # Create record
  record = RuilRequest.objects.create(
    timetableduty=duty,
    user=request.user,
    comments=request.POST.get("comments", "")
  )

  # inform team leader
  template = get_template('email/ruilverzoek.txt')

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

  from_email = request.profile.email
  if from_email is None or len(from_email) == 0:
    from_email = settings.DEFAULT_FROM_EMAIL

  send_mail("Ruilverzoek", message, from_email, duty.timetable.team.leader_email())

  # Redirect to timetable-detail page to prevent re-submitting and to show the changes
  return redirect('timetable-detail-page', id=id)


@login_required
def calendar(request):
  return render(request, 'calendar.html')

urls = [
  url(r'^roosters/ruilen/(?P<id>\d+)/$', timetable_ruilen, name='timetable-ruilen'),
  url(r'^roosters/ruilen-intrekken/(?P<id>\d+)/$', timetable_undo_ruilen, name='timetable-undo-ruilen'),
  url(r'^roosters/(?P<id>\d+)/$', timetables, name='timetable-detail-page'),
  url(r'^roosters/$', timetables, name='timetable-list-page'),
  url(r'^kalender/$', calendar, name='calendar-page'),
  url(r'^kalendar/nieuw/$', add_event, name='add-event-page'),
]
