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

def uniqify(seq, idfun=None):
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result


@login_required
def add_event(request):
  return render(request, 'add_event.html', {})

@login_required
@require_POST
def add_event_post(request):
  date = str(request.POST.get("date", ""))

  # Ochtenddienst
  startdate = "%s 09:30:00" % date
  enddate = "%s 11:00:00" % date
  title = "Ochtenddienst"
  service = Service.objects.create(
    startdatetime=startdate,
    enddatetime=enddate,
    owner=request.profile,
    title=title,
    timetable=Timetable.objects.get(title="Diensten"),
    minister=str(request.POST.get("minister", ""))
  )

  # Middagdienst
  if request.POST.get("zomertijd", False):
    startdate = "%s 18:30:00" % date
    enddate = "%s 19:30:00" % date
    title = "Avonddienst"
  else:
    startdate = "%s 16:30:00" % date
    enddate = "%s 17:30:00" % date
    title = "Middagdienst"

  service = Service.objects.create(
    startdatetime=startdate,
    enddatetime=enddate,
    owner=request.profile,
    title=title,
    timetable=Timetable.objects.get(title="Diensten"),
    minister=str(request.POST.get("minister", ""))
  )

  return redirect('add-event-page')


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
      .filter(event__enddatetime__gte=datetime.today().date())\
      .order_by("event__startdatetime", "event__enddatetime")

    if request.profile.teamleader_of(table.team):
      table.groepsbeheer = True

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
    'notmytables': notmytables,
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
    'sendtime': datetime.now(),
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
    'comments': comments,
    'sendtime': datetime.now(),
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
    'team': table.team,
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

  # Get all teammembers
  members = ruil.timetableduty.timetable.team.teammembers.all()

  # set default selection to member which is last scheduled
  duties = ruil.timetableduty.timetable.duties.filter(event__enddatetime__gte=datetime.today().date()).order_by("-event__enddatetime", "-event__startdatetime")
  if duties.exists():
    responsibles = duties.values_list('responsible', flat=True)
    print(responsibles)
    unique_responsibles = uniqify(responsibles)
    selected_member = unique_responsibles[-1]
  else:
    selected_member = 0

  # Render that stuff!
  return render(request, 'ruilverzoek.html', {
    'ruil': ruil,
    'members': members,
    'selected_member': selected_member
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


# Duties inplannen/wijzigen

@login_required
def timetable_teamleader_duty_add(request):
  table = Timetable.objects.get(pk=request.POST.get("timetable", ""))

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(table.team):
    # Show error (no access) page
    return HttpResponse(status=404)

  event = Event.objects.get(pk=request.POST.get("event", ""))
  responsible = Profile.objects.get(pk=request.POST.get("responsible", ""))

  # Create new duty
  TimetableDuty.objects.create(
    timetable=table,
    event=event,
    responsible=responsible,
    comments=request.POST.get("comments", "")
  )

  return redirect('timetable-teamleader-page', id=table.id)

@login_required
def timetable_teamleader_duty_edit_save(request, id):
  duty = TimetableDuty.objects.get(pk=id)

  if not request.POST.get("timetable", "") or isinstance(request.POST.get("timetable", ""), int):
    table = duty.timetable
  else:
    table = Timetable.objects.get(pk=request.POST.get("timetable", ""))

  # Check if user is teamleader of the new/old timetable's team
  if not request.profile.teamleader_of(table.team) or not request.profile.teamleader_of(duty.timetable.team):
    # Show error (no access) page
    return HttpResponse(status=404)

  event = Event.objects.get(pk=request.POST.get("event", ""))
  responsible = Profile.objects.get(pk=request.POST.get("responsible", ""))

  # Edit duty
  duty.timetable = table
  duty.event = event
  duty.responsible = responsible
  duty.comments = request.POST.get("comments", "")

  duty.save()

  return redirect('timetable-detail-page', id=table.id)

@login_required
def timetable_teamleader_duty_edit(request, id):
  duty = TimetableDuty.objects.get(pk=id)

  # Return only tables which the user is admin of
  # Get all teams which the user is leader of
  leading_teams = TeamMember.objects.filter(profile=request.profile,role='LEI').prefetch_related('team')

  # Get all corresponding timetables
  tables = Timetable.objects.filter(team__in=leading_teams.values('team'))

  # Get all future events
  events = Event.objects.filter(startdatetime__gte=datetime.today().date())\
      .order_by("startdatetime", "enddatetime", "title")

  # Get all teammembers
  members = TeamMember.objects.filter(team=duty.timetable.team)

  return render(request, 'teamleader_duty_edit.html', {
    'duty': duty,
    'table': duty.timetable,
    'tables': tables,
    'events': events,
    'members': members,
    'selected_event': duty.event.pk,
    'selected_responsible': duty.responsible.pk,
  })

@login_required
def timetable_teamleader_duty_delete(request, id):
  duty = TimetableDuty.objects.get(pk=id)
  table = duty.timetable
  duty.delete()

  return redirect('timetable-detail-page', id=table.pk)

@login_required
def timetable_teamleader_duty_new(request, id):
  table = Timetable.objects.get(pk=id)

  # Get all future events
  events = Event.objects.filter(startdatetime__gte=datetime.today().date())\
      .order_by("startdatetime", "enddatetime", "title")

  # set default selection to event without duty (belonging to this timetable)
  if events.exclude(duties__timetable=table.pk).exists():
    selected_event = events.exclude(duties__timetable=table.pk).first().pk
  else:
    selected_event = 0

  # Get all teammembers
  members = table.team.teammembers.all()

  # set default selection to member which is last scheduled
  duties = table.duties.filter(event__enddatetime__gte=datetime.today().date()).order_by("-event__enddatetime", "-event__startdatetime")
  if duties.exists():
    responsibles = duties.values_list('responsible', flat=True)
    print(responsibles)
    unique_responsibles = uniqify(responsibles)
    selected_member = unique_responsibles[-1]
  else:
    selected_member = 0

  return render(request, 'teamleader_duty.html', {
    'table': table,
    'events': events,
    'members': members,
    'selected_event': selected_event,
    'selected_member': selected_member,
  })


# Calendar

@login_required
def calendar(request):
  return render(request, 'calendar.html')

# When editting URLs, pay attention for the Ajax call in app.jsx -> window.timetableMain()
urls = [
  url(r'^roosters/ruilverzoek/new/(?P<id>\d+)/$', timetable_ruilen, name='timetable-ruilen'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/intrekken/$', timetable_undo_ruilen, name='timetable-undo-ruilen'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/afwijzen/$', timetable_undo_ruilen_teamleader, name='timetable-undo-ruilen-teamleader'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/accept/$', timetable_ruilverzoek_accept, name='timetable-ruilverzoek-accept'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/$', timetable_ruilverzoek, name='timetable-ruilverzoek'),

  url(r'^roosters/teamleider/duty/add/$', timetable_teamleader_duty_add, name='timetable-teamleader-duty-add'),
  url(r'^roosters/teamleider/duty/(?P<id>\d+)/edit/save/$', timetable_teamleader_duty_edit_save, name='timetable-teamleader-duty-edit-save'),
  url(r'^roosters/teamleider/duty/(?P<id>\d+)/edit/$', timetable_teamleader_duty_edit, name='timetable-teamleader-duty-edit'),
  url(r'^roosters/teamleider/duty/(?P<id>\d+)/delete/$', timetable_teamleader_duty_delete, name='timetable-teamleader-duty-delete'),
  url(r'^roosters/(?P<id>\d+)/teamleider/duty/new/$', timetable_teamleader_duty_new, name='timetable-teamleader-duty-new'),

  url(r'^roosters/(?P<id>\d+)/teamleider/$', timetable_teamleader, name='timetable-teamleader-page'),

  url(r'^roosters/(?P<id>\d+)/$', timetables, name='timetable-detail-page'),
  url(r'^roosters/$', timetables, name='timetable-list-page'),

  url(r'^kalender/$', calendar, name='calendar-page'),
  url(r'^kalender/nieuw/post/$', add_event_post, name='add-event-post'),
  url(r'^kalender/nieuw/$', add_event, name='add-event-page'),
]
