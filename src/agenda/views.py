from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import *
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.conf import settings
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.sites.shortcuts import get_current_site
import random
import logging
import re

from .models import *
from base.models import Profile, Family
from .forms import *

logger = logging.getLogger(__name__)

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
def timetables(request, id=None):

  # Get all the tables linked to the team(s) the user is in
  mytables = list(Timetable\
    .objects\
    .filter(Q(team__teammembers__profile__pk=request.profile.pk) | Q(team__teammembers__family__pk=request.profile.family.pk))\
    .exclude(team__isnull=True))

  mytables = uniqify(mytables)

  # Insert special buttons for special persons (teamleaders)
  for table in mytables:
    if request.profile.teamleader_of(table.team):
      table.groepsbeheer = True

  # Get the first-to-see table id
  if id is None and len(mytables) > 0:
    id = mytables[0].pk

  # Get current table
  #table = Timetable.objects.prefetch_related('team__members').filter(pk=id).first()
  table = Timetable.objects.filter(pk=id).first()

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
      if req.profile == duty.responsible or req.profile.family == duty.responsible_family:
        duty.ruilrequest = req

  # Get all the other tables
  # that are not really relevant to the user
  # also filter out special tables, like Diensten
  notmytables = list(Timetable\
    .objects\
    .exclude(team__members__pk=request.profile.pk)\
    .exclude(team__teammembers__family__pk=request.profile.family.pk)\
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
  if not request.profile.teamleader_of(req.timetableduty.timetable.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=req_id)

  # Only send email if eventdate > currentdate
  if req.timetableduty.event.startdatetime > datetime.now():
    # Send notification email to the user
    templateTXT = get_template('email/ruilverzoek_status.txt')
    templateHTML = get_template('email/ruilverzoek_status.html')

    data = Context({
      'resp': req.profile,
      'status': 'afgewezen of geannuleerd',
      'duty': req.timetableduty,
      'protocol': 'https',
      'domain': get_current_site(None).domain,
      'sendtime': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
    })

    messageTXT = templateTXT.render(data)
    messageHTML = templateHTML.render(data)

    from_email = settings.DEFAULT_FROM_EMAIL

    to_emails = [req.profile.email, ]
    send_mail("Ruilverzoek afgewezen", messageTXT, from_email, to_emails, html_message=messageHTML)

  # delete the request
  req.delete()

  return redirect('timetable-teamleader-page', id=req_id)

@login_required
@require_POST
def timetable_ruilen(request, id):
  duty = TimetableDuty.objects.get(pk=id)
  comments = request.POST.get("comments", "").strip()

  # Create record
  record = RuilRequest.objects.create(
    timetableduty=duty,
    profile=request.profile,
    comments=comments
  )

  # inform team leader
  templateTXT = get_template('email/ruilverzoek.txt')
  templateHTML = get_template('email/ruilverzoek.html')

  data = Context({
    'resp': request.profile,
    'duty': duty,
    'comments': comments,
    'protocol': 'https',
    'domain': get_current_site(None).domain,
    'sendtime': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
  })

  messageTXT = templateTXT.render(data)
  messageHTML = templateHTML.render(data)

  #from_email = request.profile.email
  #if from_email is None or len(from_email) == 0:
  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [ t[0] for t in duty.timetable\
                                  .team.leaders()\
                                  .exclude(profile__email=None)
                                  .values_list('profile__email') ]

  send_mail("Ruilverzoek", messageTXT, from_email, to_emails, html_message=messageHTML)

  # Redirect to timetable-detail page to prevent re-submitting and to show the changes
  return redirect('timetable-detail-page', id=duty.timetable.id)


@login_required
def timetable_teamleader(request, id):
  # Get current table
  table = Timetable.objects.prefetch_related('team__members').get(pk=id)

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(table.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=id)

  # OK, user is teamleader, let's continue:

  #
  # Ruil requests
  #
  ruils = RuilRequest.objects.filter(timetableduty__timetable=id)

  #
  # New duty
  #

  # Get all future events
  events = Event.objects.filter(startdatetime__gte=datetime.today().date())\
    .order_by("startdatetime", "enddatetime", "title")

  # set default selection to event without duty (belonging to this timetable)
  if events.exclude(duties__timetable=table.pk).exists():
    selected_event = events.exclude(duties__timetable=table.pk).first().pk
  else:
    selected_event = 0

  # Get all teammembers
  profiles = table.team.teammembers.filter(family=None).order_by('profile__first_name', 'profile__last_name', 'profile__birthday')
  # Get all teamfamilies
  families = table.team.teammembers.filter(profile=None)

  members = table.team.teammembers.values_list('profile', 'family')

  # Look only in the past `limit` duties
  limit = 2 * len(members)
  duties = table.duties.order_by("-event__enddatetime", "-event__startdatetime")[:limit]

  # set default selection to member which is last scheduled
  if len(duties):
    profiles_values = profiles.values_list('profile', flat=True)
    families_values = families.values_list('family', flat=True)

    resps = []
    # get only users that are still teammembers
    for d in duties:
      if d.responsible and d.responsible.pk in profiles_values:
        resps.append((d.responsible.pk, None))
      elif d.responsible_family and d.responsible_family.pk in families_values:
        resps.append((None, d.responsible_family.pk))

    # Add remaining members
    # This is a list with all members of the past `limit` duties, ordered by time
    resps = uniqify(list(resps) + list(members))

    lastone = resps[-1]
    if lastone[0] is None:
      selected_family = lastone[1]
      selected_member = 0
    else:
      selected_family = 0
      selected_member = lastone[0]

  else:
    selected_member = 0
    selected_family = 0

  # Render that stuff!
  return render(request, 'teamleader/teamleader.html', {
    'table': table,
    'ruils': ruils,
    'team': table.team,
    'events': events,
    'members': profiles,
    'families': families,
    'selected_event': selected_event,
    'selected_member': selected_member,
    'selected_family': selected_family,
  })

@login_required
def timetable_ruilverzoek(request, id):
  # Get current ruilrequeset
  ruil = RuilRequest.objects.get(pk=id)

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(ruil.timetableduty.timetable.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=ruil.timetableduty.timetable.team.pk)

  # OK, user is teamleader, let's continue:

  # Get all teammembers
  profiles = ruil.timetableduty.timetable.team.teammembers.filter(family=None).order_by('profile__first_name', 'profile__last_name', 'profile__birthday')
  # Get all teamfamilies
  families = ruil.timetableduty.timetable.team.teammembers.filter(profile=None)

  members = ruil.timetableduty.timetable.team.teammembers.values_list('profile', 'family')

  # Look only in the past {limit} duties
  limit = 2 * len(members)
  # And also include next week
  maxweeks = ruil.timetableduty.event.startdatetime + timedelta(weeks=1)
  duties = ruil.timetableduty.timetable.duties.filter(event__startdatetime__lte=maxweeks).order_by("-event__enddatetime", "-event__startdatetime")[:limit]

  # set default selection to member which is last scheduled
  if len(duties):
    profiles_values = profiles.values_list('profile', flat=True)
    families_values = families.values_list('family', flat=True)

    resps = []
    # get only users that are still teammembers
    for d in duties:
      if d.responsible and d.responsible.pk in profiles_values:
        resps.append((d.responsible.pk, None))
      elif d.responsible_family and d.responsible_family.pk in families_values:
        resps.append((None, d.responsible_family.pk))

    # Add remaining members
    # This is a list with all members of the past `limit` duties, ordered by time
    resps = uniqify(list(resps) + list(members))

    lastone = resps[-1]
    if lastone[0] is None:
      selected_member = 0
      selected_family = lastone[1]
    else:
      selected_member = lastone[0]
      selected_family = 0

    # Filter out current user
    if ((ruil.timetableduty.responsible and ruil.timetableduty.responsible.pk is selected_member)\
        or (ruil.timetableduty.responsible_family and ruil.timetableduty.responsible_family.pk is selected_family))\
        and len(resps) > 1:
      lastone = resps[-2]

      if lastone[0] is None:
        selected_member = 0
        selected_family = lastone[1]
      else:
        selected_member = lastone[0]
        selected_family = 0

  else:
    selected_member = 0
    selected_family = 0

  # Render that stuff!
  return render(request, 'teamleader/ruilverzoek.html', {
    'ruil': ruil,
    'members': profiles,
    'families': families,
    'selected_member': selected_member,
    'selected_family': selected_family,
  })

@login_required
@require_POST
def timetable_ruilverzoek_accept(request, id):
  # Get current ruilrequeset
  ruil = RuilRequest.objects.get(pk=id)

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(ruil.timetableduty.timetable.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=ruil.timetableduty.timetable.team.pk)

  # OK, user is teamleader, let's continue:
  # Sent notification email  to the user
  templateTXT = get_template('email/ruilverzoek_status.txt')
  templateHTML = get_template('email/ruilverzoek_status.html')

  data = Context({
    'resp': ruil.profile,
    'status': 'geaccepteerd',
    'duty': ruil.timetableduty,
    'protocol': 'https',
    'domain': get_current_site(None).domain,
    'sendtime': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
  })

  messageTXT = templateTXT.render(data)
  messageHTML = templateHTML.render(data)

  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [ruil.profile.email, ]
  send_mail("Ruilverzoek geaccepteerd", messageTXT, from_email, to_emails, html_message=messageHTML)

  # Get selected user
  resp_id = request.POST.get("responsible")[1:]

  if request.POST.get("responsible")[0] is "f":
    prof = None
    fam = Family.objects.get(pk=resp_id)
  else:
    prof = Profile.objects.get(pk=resp_id)
    fam = None

  ruil.timetableduty.responsible = prof
  ruil.timetableduty.responsible_family = fam
  ruil.timetableduty.save()

  # Remove ruilrequest
  ruil.delete()

  return redirect('timetable-teamleader-page', id=ruil.timetableduty.timetable.id)


# Duties inplannen/wijzigen

@login_required
def timetable_teamleader_duty_add(request):
  table = Timetable.objects.get(pk=request.POST.get("timetable", ""))

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(table.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.pk)

  event = Event.objects.get(pk=request.POST.get("event", ""))

  # Get all responsibles
  resps = request.POST.getlist("responsible[]")

  if len(resps) is 0:
    messages.error(request, "Kies tenminste één persoon of familie.")
    return redirect('timetable-teamleader-page', id=table.id)

  # Create duty for each responsible
  for r in resps:
    # Strip ID
    resp_id = r[1:]

    # Strip type
    if r[0] is "f":
      prof = None
      fam = Family.objects.get(pk=resp_id)
    else:
      prof = Profile.objects.get(pk=resp_id)
      fam = None

    # Create new duty
    duty = TimetableDuty.objects.create(
      timetable=table,
      event=event,
      responsible=prof,
      responsible_family=fam,
      comments=request.POST.get("comments", "").strip()
    )

    messages.success(request, "%s is ingepland voor '%s'." % (duty.resp_name(), event))

  return redirect(reverse('timetable-teamleader-page', kwargs={'id': table.id}) + "#inplannen")

@login_required
def timetable_teamleader_duty_edit_save(request, id):
  duty = TimetableDuty.objects.get(pk=id)

  if not request.POST.get("timetable", "") or isinstance(request.POST.get("timetable", ""), int):
    table = duty.timetable
  else:
    table = Timetable.objects.get(pk=request.POST.get("timetable", ""))

  # Check if user is teamleader of the new/old timetable's team
  if (not request.profile.teamleader_of(table.team) or not request.profile.teamleader_of(duty.timetable.team)) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.team.pk)

  # Get selected user
  resp_id = request.POST.get("responsible")[1:]

  if request.POST.get("responsible")[0] is "f":
    prof = None
    fam = Family.objects.get(pk=resp_id)
  else:
    prof = Profile.objects.get(pk=resp_id)
    fam = None

  event = Event.objects.get(pk=request.POST.get("event", ""))

  # Edit duty
  duty.timetable = table
  duty.event = event
  duty.responsible = prof
  duty.responsible_family = fam
  duty.comments = request.POST.get("comments", "").strip()

  duty.save()

  messages.success(request, "Taak opgeslagen.")

  return redirect('timetable-detail-page', id=table.id)

@login_required
def timetable_teamleader_duty_edit(request, id):
  duty = TimetableDuty.objects.get(pk=id)

  # Check if user is teamleader of the new/old timetable's team
  if not request.profile.teamleader_of(duty.timetable.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=duty.timetable.team.pk)

  # Get all corresponding timetables
  if request.user.has_perm('agenda.change_timetable'):
    tables = Timetable.objects.all()
  else:
    # Return only tables which the user is admin of
    # Get all teams which the user is leader of
    leading_teams = TeamMember.objects.filter(profile=request.profile, is_admin=True).prefetch_related('team')

    tables = Timetable.objects.filter(team__in=leading_teams.values('team'))

  # Get all future events
  events = Event.objects.filter(startdatetime__gte=datetime.today().date())\
      .order_by("startdatetime", "enddatetime", "title")

  # Get all teammembers
  members = duty.timetable.team.teammembers.filter(family=None).order_by('profile__first_name', 'profile__last_name', 'profile__birthday')
  # Get all teamfamilies
  families = duty.timetable.team.teammembers.filter(profile=None)

  return render(request, 'teamleader/teamleader_duty_edit.html', {
    'duty': duty,
    'table': duty.timetable,
    'tables': tables,
    'events': events,
    'members': members,
    'families': families,
    'selected_event': duty.event.pk,
  })

@login_required
def timetable_teamleader_duty_delete(request, id):
  duty = TimetableDuty.objects.get(pk=id)
  table = duty.timetable

  # Check if user is teamleader of the new/old timetable's team
  if not request.profile.teamleader_of(table.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.team.pk)

  duty.delete()

  return redirect('timetable-detail-page', id=table.pk)

#  Not being used anymore, because it's integrated in the main teamleader page
#
# @login_required
# def timetable_teamleader_duty_new(request, id):
#   table = Timetable.objects.get(pk=id)
#
#   # Check if user is teamleader of the new/old timetable's team
#   if not request.profile.teamleader_of(table.team) and not request.user.has_perm('agenda.change_timetable'):
#     # Redirect to first public page
#     return redirect('timetable-detail-page', id=table.team.pk)
#
#   # Get all future events
#   events = Event.objects.filter(startdatetime__gte=datetime.today().date())\
#       .order_by("startdatetime", "enddatetime", "title")
#
#   # set default selection to event without duty (belonging to this timetable)
#   if events.exclude(duties__timetable=table.pk).exists():
#     selected_event = events.exclude(duties__timetable=table.pk).first().pk
#   else:
#     selected_event = 0
#
#   # Get all teammembers
#   members = table.team.teammembers
#
#   # set default selection to member which is last scheduled
#   duties = table.duties.filter(event__enddatetime__gte=datetime.today().date()).order_by("-event__enddatetime", "-event__startdatetime")
#   if duties.exists():
#     # get only users that are still teammembers
#     responsibles = duties.filter(responsible__in=members.values_list('profile', flat=True)).values_list('responsible', flat=True)
#
#     unique_responsibles = uniqify(responsibles)
#
#     # Add also the members who aren't scheduled for any duty yet
#     b = members.values_list('profile', flat=True)
#     all_responsibles = uniqify(unique_responsibles + uniqify(b))
#
#     selected_member = all_responsibles[-1]
#   else:
#     selected_member = 0
#
#   return render(request, 'teamleader/teamleader_duty.html', {
#     'table': table,
#     'events': events,
#     'members': members,
#     'selected_event': selected_event,
#     'selected_member': selected_member,
#   })


# Calendar

@login_required
def calendar(request):
  return render(request, 'calendar.html')

# When editting URLs, pay attention for the Ajax call in app.jsx -> window.timetableMain()

@login_required
@permission_required('agenda.add_service', raise_exception=True)
def services_admin(request):
  # set default date to next sunday without a service
  # Get last sunday service
  last = Service.objects.filter(startdatetime__week_day=1).order_by('-startdatetime').first()

  # Add one week
  if last:
    startdatetime = last.startdatetime + timedelta(weeks=1)
  else:
    # Get next upcoming sunday
    today = datetime.today().date()
    startdatetime = today + timedelta(days=-today.weekday()-1, weeks=1)

  return render(request, 'services/admin.html', {
    'startdatetime': startdatetime,
  })

@login_required
@require_POST
@permission_required('agenda.add_service', raise_exception=True)
def services_admin_add(request):
  date = str(request.POST.get("date", ""))

  # Ochtenddienst
  startdate = "%s %s:00" % (date, str(request.POST.get("starttime1", "09:30")))
  enddate = "%s %s:00" % (date, str(request.POST.get("endtime1", "11:00")))

  try:
    startdate = datetime.strptime(startdate, '%d-%m-%Y %H:%M:%S')
    enddate = datetime.strptime(enddate, '%d-%m-%Y %H:%M:%S')
  except ValueError:
    messages.error(request, 'Het formaat van de ingevulde datum en/of tijdstip klopt niet.')
    return redirect('services-admin')

  Service.objects.create(
    startdatetime=startdate,
    enddatetime=enddate,
    owner=request.profile,
    title=request.POST.get("title1", "").strip(),
    timetable=Timetable.objects.get(title="Diensten"),
    minister=request.POST.get("minister1", "").strip(),
    theme=request.POST.get("theme1", "").strip(),
    comments=request.POST.get("comments1", "").strip(),
    description=request.POST.get("description1", "").strip(),
  )

  if request.POST.get("secondservice", ""):
    # Middagdienst
    startdate = "%s %s:00" % (date, str(request.POST.get("starttime2", "16:30")))
    enddate = "%s %s:00" % (date, str(request.POST.get("endtime2", "17:45")))

    try:
      startdate = datetime.strptime(startdate, '%d-%m-%Y %H:%M:%S')
      enddate = datetime.strptime(enddate, '%d-%m-%Y %H:%M:%S')
    except ValueError:
      messages.error(request, 'Het formaat van de ingevulde datum en/of tijdstip klopt niet.')
      return redirect('services-admin')

    Service.objects.create(
      startdatetime=startdate,
      enddatetime=enddate,
      owner=request.profile,
      title=request.POST.get("title2", "").strip(),
      timetable=Timetable.objects.get(title="Diensten"),
      minister=request.POST.get("minister2", "").strip(),
      theme=request.POST.get("theme2", "").strip(),
      comments=request.POST.get("comments2", "").strip(),
      description=request.POST.get("description2", "").strip(),
    )

    messages.success(request, "Diensten zijn toegevoegd.")
  else:
    messages.success(request, "Dienst is toegevoegd.")

  return redirect('services-admin')

@login_required
@require_POST
@permission_required('agenda.change_service', raise_exception=True)
def services_admin_edit_save(request, id):
  service = Service.objects.get(pk=id)

  date = str(request.POST.get("date", service.startdatetime.date()))

  # Ochtenddienst
  startdate = "%s %s:00" % (date, str(request.POST.get("starttime", service.startdatetime.time())))
  enddate = "%s %s:00" % (date, str(request.POST.get("endtime", service.enddatetime.time())))

  try:
    startdate = datetime.strptime(startdate, '%d-%m-%Y %H:%M:%S')
    enddate = datetime.strptime(enddate, '%d-%m-%Y %H:%M:%S')
  except ValueError:
    messages.error(request, 'Het formaat van de ingevulde datum en/of tijdstip klopt niet.')
    return redirect('services-admin')

  service.startdatetime = startdate
  service.enddatetime = enddate
  service.title = request.POST.get("title", "").strip()
  service.minister = request.POST.get("minister", "").strip()
  service.theme = request.POST.get("theme", "").strip()
  service.comments = request.POST.get("comments", "").strip()
  service.description = request.POST.get("description", "").strip()

  service.save()

  messages.success(request, "Dienst is opgeslagen.")

  return redirect('services-admin')

@login_required
@permission_required('agenda.change_service', raise_exception=True)
def services_admin_edit(request, id):

  return render(request, 'services/edit.html', {
    'service': Service.objects.get(pk=id),
  })

@login_required
@permission_required('agenda.delete_service', raise_exception=True)
def services_admin_delete(request, id):
  Service.objects.get(pk=id).delete()

  # Delete all duties of this service
  TimetableDuty.objects.filter(event=id).delete()

  messages.success(request, "Dienst is verwijderd.")

  return redirect('services-admin')



# Team pages

@login_required
def teampage_control_members(request, id):
  team = Team.objects.get(pk=id)

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=id)

  members = team.teammembers.order_by('family__lastname', 'profile__first_name')

  roles = TeamMemberRole.objects.active().order_by('name')

  # Render that stuff!
  return render(request, 'teampage/teampage_control_members.html', {
    'team': team,
    'members': members,
    'roles': roles,
    'selected_role': 'LID',
  })

@login_required
@require_POST
def teampage_control_members_add(request):
  team = request.POST.get("team", "")
  profile = request.POST.get("profile", "0")
  family = request.POST.get("family", "0")

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=team.pk)

  # Check if profile is valid
  if family is "0" and TeamMember.objects.filter(team_id=team, profile_id=profile).exists():
    messages.error(request, "Het gekozen lid maakt al deel uit van dit team.")
    return redirect('teampage-control-members', id=team)

  # Check if profile is valid
  if profile is "0" and TeamMember.objects.filter(team_id=team, family_id=family).exists():
    messages.error(request, "De gekozen familie maakt al deel uit van dit team.")
    return redirect('teampage-control-members', id=team)

  if Profile.objects.filter(pk=profile).exists():
    prof = Profile.objects.get(pk=profile)
    fam = None
  elif Family.objects.filter(pk=family).exists():
    prof = None
    fam = Family.objects.get(pk=family)
  else:
    messages.error(request, "Er is geen (geldig) lid/familie gekozen om toe te voegen.")
    return redirect('teampage-control-members', id=team)

  TeamMember.objects.create(
    team=Team.objects.get(pk=team),
    profile=prof,
    family=fam,
    role=TeamMemberRole.objects.get(pk=request.POST.get("role", "")),
    is_admin=True if request.POST.get("is_admin", False) else False
  )

  messages.success(request, "Het nieuwe teamlid is toegevoegd.")

  return redirect('teampage-control-members', id=team)

@login_required
@require_POST
def teampage_control_members_edit_save(request, id):
  member = TeamMember.objects.get(pk=id)

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(member.team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=member.team.pk)

  member.role = TeamMemberRole.objects.get(pk=request.POST.get("role", ""))
  member.is_admin = True if request.POST.get("is_admin", False) else False
  member.save()

  messages.success(request, "De wijzigingen zijn opgeslagen.")

  return redirect('teampage-control-members', id=member.team.pk)

@login_required
def teampage_control_members_edit(request, id):
  member = TeamMember.objects.get(pk=id)

  roles = TeamMemberRole.objects.active().order_by('name')

  # Render that stuff!
  return render(request, 'teampage/teampage_control_members_edit.html', {
    'team': member.team,
    'member': member,
    'roles': roles,
  })

@login_required
def teampage_control_members_delete(request, id):
  member = TeamMember.objects.get(pk=id)

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(member.team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=id)

  team = member.team.pk
  member.delete()

  messages.success(request, "Het teamlid is verwijderd.")

  return redirect('teampage-control-members', id=team)


@login_required
def teampage_control_timetables(request, id):
  team = Team.objects.get(pk=id)

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=id)

  tables = team.timetables

  return render(request, 'teampage/control_timetables.html', {
    'team': team,
    'tables': tables,
    'random_color': '{:06x}'.format(random.randint(0, 0xffffff)),
  })

@login_required
@require_POST
def teampage_control_timetables_add(request):
  team = Team.objects.get(pk=request.POST.get("team", ""))

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=team.pk)

  if request.POST.get("color", "")[0] is "#":
    color = request.POST.get("color", "")[1:]
  else:
    color = request.POST.get("color", "")

  if len(team.timetables.all()) and not request.user.has_perm('agenda.change_team'):
    messages.error(request, "Je hebt al een rooster voor dit team toegevoegd. Het limiet staat op één rooster per team.")
    return redirect('teampage-control-timetables', id=team.pk)

  Timetable.objects.create(
    team=team,
    owner=request.profile,
    title=request.POST.get("title", "").strip(),
    description=request.POST.get("description", "").strip(),
    incalendar=request.POST.get("incalendar", ""),
    color=color,
  )

  messages.success(request, "Het rooster is toegevoegd.")

  return redirect('teampage-control-timetables', id=team.pk)

@login_required
def teampage_control_timetables_delete(request, id):
  table = Timetable.objects.get(pk=id)
  team = table.team.pk

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(table.team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=team)

  table.delete()

  messages.success(request, "Het rooster is verwijderd.")

  return redirect('teampage-control-timetables', id=team)

@login_required
def teampage_control_timetables_edit(request, id):
  table = Timetable.objects.get(pk=id)

  return render(request, 'teampage/control_timetables_edit.html', {
    'table': table,
  })

@login_required
@require_POST
def teampage_control_timetables_edit_save(request, id):
  table = Timetable.objects.get(pk=id)

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(table.team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=table.team.pk)

  if request.POST.get("color", "")[0] is "#":
    color = request.POST.get("color", "")[1:]
  else:
    color = request.POST.get("color", "")

  table.title = request.POST.get("title", "").strip()
  table.description = request.POST.get("description", "").strip()
  table.incalendar = request.POST.get("incalendar", "")
  table.color = color
  table.save()

  messages.success(request, "Het rooster is opgeslagen.")

  return redirect('teampage-control-timetables', id=table.team.pk)


@login_required
@require_POST
def teampage_control_edit_save(request, id):
  team = Team.objects.get(pk=id)

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=id)

  email = request.POST.get("email", "").lower().strip()

  if not email is "":
    try:
      validate_email(email)
    except ValidationError:
      messages.error(request, "Het opgegeven e-mailadres is niet geldig.")
      return redirect('teampage-control-edit', id=team.pk)

  # Remove empty lines at the beginning/end
  remindermail = request.POST.get("remindermail", "")
  # Remove end
  remindermail = re.sub('(<p>&nbsp;</p>[\n\r]*)*$', '', remindermail)
  # Remove begin
  remindermail = re.sub('^(<p>&nbsp;</p>[\n\r]*)*', '', remindermail)

  description = request.POST.get("description", "").strip()
  # Remove end
  description = re.sub('(<p>&nbsp;</p>[\n\r]*)*$', '', description)
  # Remove begin
  description = re.sub('^(<p>&nbsp;</p>[\n\r]*)*', '', description)

  team.name = request.POST.get("name", "").strip()
  team.email = email
  team.description = description.strip()
  team.remindermail = remindermail.strip()
  team.save()

  messages.success(request, "De instellingen zijn opgeslagen.")

  return redirect('teampage', id=team.pk)

@login_required
def teampage_control_edit(request, id):
  team = Team.objects.get(pk=id)

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=id)

  return render(request, 'teampage/edit.html', {
    'team': team,
    'form': TeamForm(instance=team),
  })

@login_required
def teampage(request, id):
  team = Team.objects.get(pk=id)

  members = team.teammembers.order_by('role__name', 'family__lastname', 'profile__first_name')

  tables = team.timetables.order_by('title')

  # Get teammembership of user
  teammember = request.profile.team_membership.filter(team=team).first()

  # Check if this person is the head of the family: getting the reminder-mails
  if request.profile == request.profile.family.members_sorted()[0]:
    teammember_family = request.profile.family.team_membership.filter(team=team).first()
  else:
    teammember_family = None

  # Render that stuff!
  return render(request, 'teampage/teampage.html', {
    'team': team,
    'is_admin': request.profile.teamleader_of(team),
    'teammember': teammember,
    'teammember_family': teammember_family,
    'members': members,
    'tables': tables,
  })

@login_required
@permission_required('agenda.add_team', raise_exception=True)
def globalteampage(request):

  return render(request, 'globalteamadmin.html')

@login_required
@permission_required('agenda.add_team', raise_exception=True)
@require_POST
def globalteampage_add(request):
  email = request.POST.get("email", "").lower()

  if not email is "":
    try:
      validate_email(email)
    except ValidationError:
      messages.error(request, "Het opgegeven e-mailadres is niet geldig.")
      return redirect('team-add')

  name = request.POST.get("name", "").strip()

  if name is "":
    messages.error(request, "Er moet een naam voor het team ingevuld zijn.")
    return redirect('team-add')

  team = Team.objects.create(
    name=name,
    description=request.POST.get("description", "").strip(),
    email=email,
  )

  messages.success(request, "Team is toegevoegd.")

  return redirect('team-list-page')

@login_required
@permission_required('agenda.delete_team', raise_exception=True)
def globalteampage_delete(request, id):
  team = Team.objects.get(pk=id)

  # Delete timetable
  for table in team.timetables.all():
    name = table.title
    table.delete()

    messages.success(request, (" - Het rooster '%s' van team '%s' is verwijderd." % (name, team.name)))

  # Delete team
  name = team.name
  team.delete()

  messages.success(request, ("Team '%s' is verwijderd." % (name)))

  return redirect('team-list-page')

@login_required
@permission_required('agenda.add_eventfile', raise_exception=True)
def services_files_admin(request, id=None):

  ef = None

  # Get some recent services
  maxweeks = datetime.today().date() - timedelta(weeks=3)
  recent_services = Service.objects.filter(startdatetime__gte=maxweeks, startdatetime__lt=datetime.today().date()) \
    .order_by("startdatetime", "enddatetime", "title")

  # Get all future services
  services = Service.objects.filter(startdatetime__gte=datetime.today().date()) \
    .order_by("startdatetime", "enddatetime", "title")

  # set default selection to event without duty (belonging to this timetable)
  if id:
    # Load EventFile
    ef = EventFile.objects.get(pk=int(id))

    selected_service = ef.event.pk

  else:
    if services.filter(files=None).exists():
      selected_service = services.filter(files=None).first().pk
    else:
      selected_service = services.first().pk

  maxweeks = datetime.today().date() - timedelta(weeks=2)
  efs = EventFile.objects.filter(event__startdatetime__gte=maxweeks) \
    .order_by("-event__startdatetime", "-event__enddatetime", "event__title", "event__pk", "title")

  return render(request, 'services/files_add.html', {
    'recent_services': recent_services,
    'services': services,
    'selected_service': selected_service,
    'ef': ef,
    'efs': efs,
    'maxweeks': maxweeks
  })

@login_required
@permission_required('agenda.add_eventfile', raise_exception=True)
@require_POST
def services_files_admin_add(request):

  # Set default title
  if not request.POST.get('title', ''):
    request.POST['title'] = str(request.FILES.get('file'))

  form = UploadEventFileForm(request.POST, request.FILES)
  

  if form.is_valid():
    # Save object
    fs = form.save(commit=False)

    fs.owner = request.profile

    fs.save()

    messages.success(request, "Bestand is opgeslagen.")
  else:
    messages.error(request, "Vul alle velden in.")

  return redirect('services-files-admin')

@login_required
@permission_required('agenda.change_eventfile', raise_exception=True)
@require_POST
def services_files_admin_edit_save(request, id):

  ef = EventFile.objects.get(pk=id)

  if request.FILES.get('file'):
    # New file, so delete old one
    ef.file.delete()

  # Create update form
  form = UploadEventFileForm(request.POST, request.FILES, instance=ef)

  if form.is_valid():
    # Save object
    form.save()

    messages.success(request, "Bestand is opgeslagen.")
  else:
    messages.error(request, "Vul alle velden in.")
    return redirect('services-files-admin-edit', id=id)

  return redirect('services-files-admin')

@login_required
@permission_required('agenda.delete_eventfile', raise_exception=True)
def services_files_admin_delete(request, id):

  ef = EventFile.objects.get(pk=id).delete()

  messages.success(request, 'Bestand is verwijderd.')

  return redirect('services-files-admin')


@login_required
def services_page(request):
  # set default date to next sunday without a service
  # Get last sunday service
  last = Service.objects.filter(startdatetime__week_day=1).order_by('-startdatetime').first()

  # Add one week
  if last:
    startdatetime = last.startdatetime + timedelta(weeks=1)
  else:
    # Get next upcoming sunday
    today = datetime.today().date()
    startdatetime = today + timedelta(days=-today.weekday()-1, weeks=1)

  return render(request, 'services/list.html', {
    'startdatetime': startdatetime,
  })

@login_required
def services_single(request, id):
  service = Service.objects.get(pk=id)

  return render(request, 'services/single.html', {
    'service': service,
  })


@login_required
@require_POST
def teampage_settings_save(request, id):
  teammember = request.profile.team_membership.filter(team__pk=id).first()
  teammember_family = request.profile.family.team_membership.filter(team__pk=id).first()

  # Check some things first
  if not teammember and not teammember_family:
    messages.error(request, "Je instellingen kunnen niet opgeslagen worden, want je bent geen lid van dit team.")
    return redirect('teampage', id=id)

  # Change values
  if teammember:
    if request.POST.get('reminder'):
      teammember.get_mail = True
    else:
      teammember.get_mail = False

    # Save it
    teammember.save()

  if teammember_family:
    if request.POST.get('reminder-family'):
      teammember_family.get_mail = True
    else:
      teammember_family.get_mail = False

    # Save it
    teammember_family.save()

  messages.success(request, "Je instellingen zijn opgeslagen.")

  return redirect('teampage', id=id)


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

  url(r'^roosters/(?P<id>\d+)/teamleider/$', timetable_teamleader, name='timetable-teamleader-page'),

  url(r'^roosters/(?P<id>\d+)/$', timetables, name='timetable-detail-page'),

  url(r'^roosters$', RedirectView.as_view(url='roosters/', permanent=True)),
  url(r'^roosters/$', timetables, name='timetable-list-page'),

  url(r'^kalender$', RedirectView.as_view(url='kalender/', permanent=True)),
  url(r'^kalender/$', calendar, name='calendar-page'),

  url(r'^team/leden/add/$', teampage_control_members_add, name='teampage-control-members-add'),
  url(r'^team/leden/(?P<id>\d+)/edit/save/$', teampage_control_members_edit_save, name='teampage-control-members-edit-save'),
  url(r'^team/leden/(?P<id>\d+)/edit/$', teampage_control_members_edit, name='teampage-control-members-edit'),
  url(r'^team/leden/(?P<id>\d+)/delete/$', teampage_control_members_delete, name='teampage-control-members-delete'),
  url(r'^team/(?P<id>\d+)/leden/$', teampage_control_members, name='teampage-control-members'),

  url(r'^team/roosters/add/$', teampage_control_timetables_add, name='teampage-control-timetables-add'),
  url(r'^team/roosters/(?P<id>\d+)/delete/$', teampage_control_timetables_delete, name='teampage-control-timetables-delete'),
  url(r'^team/roosters/(?P<id>\d+)/edit/save/$', teampage_control_timetables_edit_save, name='teampage-control-timetables-edit-save'),
  url(r'^team/roosters/(?P<id>\d+)/edit/$', teampage_control_timetables_edit, name='teampage-control-timetables-edit'),
  url(r'^team/(?P<id>\d+)/roosters/$', teampage_control_timetables, name='teampage-control-timetables'),

  url(r'^team/(?P<id>\d+)/instellingen/save/$', teampage_settings_save, name='teampage-settings-save'),

  url(r'^team/(?P<id>\d+)/edit/save/$', teampage_control_edit_save, name='teampage-control-edit-save'),
  url(r'^team/(?P<id>\d+)/edit/$', teampage_control_edit, name='teampage-control-edit'),
  url(r'^team/(?P<id>\d+)/$', teampage, name='teampage'),

  url(r'^teams/(?P<id>\d+)/delete/$', globalteampage_delete, name='team-delete'),
  url(r'^teams/add/save/$', globalteampage_add, name='team-add-save'),
  url(r'^teams/add/$', globalteampage, name='team-add'),

  url(r'^roosters/diensten/beheren/toevoegen/$', services_admin_add, name='services-admin-add'),
  url(r'^roosters/diensten/beheren/(?P<id>\d+)/edit/save/$', services_admin_edit_save, name='services-admin-edit-save'),
  url(r'^roosters/diensten/beheren/(?P<id>\d+)/edit/$', services_admin_edit, name='services-admin-edit'),
  url(r'^roosters/diensten/beheren/(?P<id>\d+)/delete/$', services_admin_delete, name='services-admin-delete'),
  url(r'^roosters/diensten/beheren/$', services_admin, name='services-admin'),

  url(r'^roosters/diensten/$', services_page, name='services-page'),
  url(r'^roosters/diensten/(?P<id>\d+)/$', services_single, name='services-single'),

  url(r'^roosters/diensten/bestanden/beheren/(?P<id>\d+)/delete/$', services_files_admin_delete, name='services-files-admin-delete'),
  url(r'^roosters/diensten/bestanden/beheren/(?P<id>\d+)/edit/save/$', services_files_admin_edit_save, name='services-files-admin-edit-save'),
  url(r'^roosters/diensten/bestanden/beheren/(?P<id>\d+)/edit/$', services_files_admin, name='services-files-admin-edit'),
  url(r'^roosters/diensten/bestanden/beheren/toevoegen/$', services_files_admin_add, name='services-files-admin-add'),
  url(r'^roosters/diensten/bestanden/beheren/$', services_files_admin, name='services-files-admin'),
]
