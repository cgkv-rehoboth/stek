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
from base.models import Profile

@login_required
def add_event(request):
  return render(request, 'add_event.html', {})

@login_required
def timetables(request, id=None):

  # Get all the tables linked to the team(s) the user is in
  mytables = list(Timetable\
    .objects\
    .filter(team__members__pk=request.profile.pk)\
    .exclude(team__isnull=True))

  # Insert special buttons for special persons (teamleaders)
  for table in mytables:
    if request.profile.teamleader_of(table.team):
      table.groepsbeheer = True

  # Get the first-to-see table id
  if id is None and len(mytables) > 0:
    id = mytables[0].pk

  # Get current table
  table = Timetable.objects.prefetch_related('team__members').filter(pk=id).first()

  # Get duties
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
      if req.profile == duty.responsible:
        duty.ruilrequest = req

  # Get all the other tables
  # that are not really relevant to the user
  notmytables = list(Timetable\
    .objects\
    .exclude(team__members__pk=request.profile.pk)\
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
  # Delete by user himself
  req = RuilRequest.objects.prefetch_related('timetableduty__timetable').get(pk=id)
  req_id = req.timetableduty.timetable.pk

  # delete the request
  req.delete()

  return redirect('timetable-detail-page', id=req_id)

@login_required
def timetable_undo_ruilen_teamleader(request, id):
  # Delete by teamleader
  req = RuilRequest.objects.prefetch_related('timetableduty__timetable').get(pk=id)
  req_id = req.timetableduty.timetable.pk

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(req.timetableduty.timetable.team):
    # Show error (no access) page
    return HttpResponse(status=404)

  # Send notification email to the user
  template = get_template('email/ruilverzoek_status.txt')

  data = Context({
    'name': req.profile.name,
    'status': 'afgewezen',
    'timetable': req.timetableduty.timetable.title,
    'duty': req.timetableduty,
  })

  message = template.render(data)

  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [ req.profile.email ]
  send_mail("Ruilverzoek user", message, from_email, to_emails)

  # delete the request
  req.delete()

  return redirect('timetable-teamleader-page', id=req_id)

@login_required
@require_POST
def timetable_ruilen(request, id):
  duty = TimetableDuty.objects.get(pk=id)

  # Create record
  record = RuilRequest.objects.create(
    timetableduty=duty,
    profile=request.profile,
    comments=request.POST.get("comments", "")
  )

  # inform team leader
  template = get_template('email/ruilverzoek.txt')

  if request.POST.get("comments"):
    comments = "Met de volgende redenen: \n %s" % request.POST.get("comments", "")
  else:
    comments = "Er is geen reden gegeven."

  data = Context({
    'name': request.profile.name,
    'timetable': duty.timetable.title,
    'duty': duty,
    'comments': comments
  })

  message = template.render(data)

  #from_email = request.profile.email
  #if from_email is None or len(from_email) == 0:
  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [ t[0] for t in duty.timetable\
                                  .team.leaders()\
                                  .values_list('profile__email') ]
  send_mail("Ruilverzoek", message, from_email, to_emails)

  # Redirect to timetable-detail page to prevent re-submitting and to show the changes
  return redirect('timetable-detail-page', id=duty.timetable.id)


@login_required
def timetable_teamleader(request, id):
  # Get current table
  table = Timetable.objects.prefetch_related('team__members').get(pk=id)

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(table.team):
    # Show error (no access) page
    return HttpResponse(status=404)

  # OK, user is teamleader, let's continue:
  # First, get all ruilrequests
  ruils = RuilRequest.objects.filter(timetableduty__timetable=id)


  # Render that stuff!
  return render(request, 'teamleader.html', {
    'table': table,
    'ruils': ruils,
  })

@login_required
def timetable_ruilverzoek(request, id):
  # Get current ruilrequeset
  ruil = RuilRequest.objects.get(pk=id)

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(ruil.timetableduty.timetable.team):
    # Show error (no access) page
    return HttpResponse(status=404)

  # OK, user is teamleader, let's continue:

  # Render that stuff!
  return render(request, 'ruilverzoek.html', {
    'ruil': ruil,
    'members': TeamMember.objects.filter(team=ruil.timetableduty.timetable.team),
  })

@login_required
@require_POST
def timetable_ruilverzoek_accept(request, id):
  # Get current ruilrequeset
  ruil = RuilRequest.objects.get(pk=id)

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(ruil.timetableduty.timetable.team):
    # Show error (no access) page
    return HttpResponse(status=404)

  # OK, user is teamleader, let's continue:
  # Sent notification email to the user
  template = get_template('email/ruilverzoek_status.txt')

  data = Context({
    'name': ruil.profile.name,
    'status': 'geaccepteerd',
    'timetable': ruil.timetableduty.timetable.title,
    'duty': ruil.timetableduty,
  })

  message = template.render(data)

  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [ ruil.profile.email ]
  send_mail("Ruilverzoek geaccepteerd", message, from_email, to_emails)

  # Change responsibility
  ruil.timetableduty.responsible = Profile.objects.get(pk=request.POST.get("vervanging"))
  ruil.timetableduty.save()

  # Remove ruilrequest
  ruil.delete()

  return redirect('timetable-teamleader-page', id=ruil.timetableduty.timetable.id)

@login_required
def calendar(request):
  return render(request, 'calendar.html')

urls = [
  url(r'^roosters/ruilen/(?P<id>\d+)/$', timetable_ruilen, name='timetable-ruilen'),
  url(r'^roosters/ruilen-intrekken/(?P<id>\d+)/$', timetable_undo_ruilen, name='timetable-undo-ruilen'),
  url(r'^roosters/ruilen-intrekken/teamleider/(?P<id>\d+)/$', timetable_undo_ruilen_teamleader, name='timetable-undo-ruilen-teamleader'),
  url(r'^roosters/(?P<id>\d+)/$', timetables, name='timetable-detail-page'),
  url(r'^roosters/teamleider/(?P<id>\d+)/$', timetable_teamleader, name='timetable-teamleader-page'),
  url(r'^roosters/ruilverzoek/accept/(?P<id>\d+)/$', timetable_ruilverzoek_accept, name='timetable-ruilverzoek-accept'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/$', timetable_ruilverzoek, name='timetable-ruilverzoek'),
  url(r'^roosters/$', timetables, name='timetable-list-page'),
  url(r'^kalender/$', calendar, name='calendar-page'),
  url(r'^kalendar/nieuw/$', add_event, name='add-event-page'),
]
