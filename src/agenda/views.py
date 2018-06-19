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
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
import random
import logging
import re
import csv
import tempfile
import json

from .models import *
from base.models import Profile, Family
from .forms import *
from .validators import *
from base.views import get_delimiter, decodeCSV

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
  mytables = list(Timetable \
                  .objects \
                  .filter(
    Q(team__teammembers__profile__pk=request.profile.pk) | Q(team__teammembers__family__pk=request.profile.family.pk)) \
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
  # table = Timetable.objects.prefetch_related('team__members').filter(pk=id).first()
  table = Timetable.objects.filter(pk=id).first()

  # Block the Diensten table from showing
  if table is not None and table.title == "Diensten":
    table = None

  # Get duties
  if table is not None:
    duties = table.duties \
      .prefetch_related('ruilen') \
      .filter(event__enddatetime__gte=datetime.today().date()) \
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
  notmytables = list(Timetable \
                     .objects \
                     .exclude(team__members__pk=request.profile.pk) \
                     .exclude(team__teammembers__family__pk=request.profile.family.pk) \
                     .exclude(team__isnull=True) \
                     .exclude(pk=id))

  # Render that stuff!
  return render(request, 'timetables.html', {
    'current_table': table,
    'duties'       : duties,
    'mytables'     : mytables,
    'notmytables'  : notmytables,
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
  if not request.profile.teamleader_of(req.timetableduty.timetable.team) and not request.user.has_perm(
      'agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=req_id)

  # Only send email if eventdate > currentdate
  if req.timetableduty.event.startdatetime > datetime.now():
    # Send notification email to the user
    templateTXT = get_template('email/ruilverzoek_status.txt')
    templateHTML = get_template('email/ruilverzoek_status.html')

    data = Context({
      'resp'    : req.profile,
      'status'  : 'afgewezen of geannuleerd',
      'duty'    : req.timetableduty,
      'protocol': 'https',
      'domain'  : get_current_site(None).domain,
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
  try:
    duty = TimetableDuty.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Taak bestaat niet.')
    return redirect('timetable-list-page')

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
    'resp'    : request.profile,
    'duty'    : duty,
    'comments': comments,
    'protocol': 'https',
    'domain'  : get_current_site(None).domain,
    'sendtime': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
  })

  messageTXT = templateTXT.render(data)
  messageHTML = templateHTML.render(data)

  # from_email = request.profile.email
  # if from_email is None or len(from_email) == 0:
  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [t[0] for t in duty.timetable \
    .team.leaders() \
    .exclude(profile__email=None)
    .values_list('profile__email')]

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
  events = Event.objects.filter(startdatetime__gte=datetime.today().date()) \
    .filter(Q(incalendar=True) | Q(incalendar=False, timetable=table)) \
    .order_by("startdatetime", "enddatetime", "title")

  # set default selection to event without duty (belonging to this timetable)
  if events.exclude(duties__timetable=table.pk).exists():
    selected_event = events.exclude(duties__timetable=table.pk).first()

    # Check if object exists
    if selected_event:
      selected_event = selected_event.pk
    else:
      selected_event = 0
  else:
    selected_event = 0

  # Get all teammembers
  profiles = table.team.teammembers.filter(family=None).order_by('profile__first_name', 'profile__last_name',
                                                                 'profile__birthday')
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
    'table'          : table,
    'ruils'          : ruils,
    'team'           : table.team,
    'events'         : events,
    'members'        : profiles,
    'families'       : families,
    'selected_event' : selected_event,
    'selected_member': selected_member,
    'selected_family': selected_family,
  })


@login_required
def timetable_ruilverzoek(request, id):
  # Get current ruilrequeset
  try:
    ruil = RuilRequest.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Ruilverzoek bestaat niet.')
    return redirect('timetable-list-page')

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(ruil.timetableduty.timetable.team) and not request.user.has_perm(
      'agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=ruil.timetableduty.timetable.team.pk)

  # OK, user is teamleader, let's continue:

  # Get all teammembers
  profiles = ruil.timetableduty.timetable.team.teammembers.filter(family=None).order_by('profile__first_name',
                                                                                        'profile__last_name',
                                                                                        'profile__birthday')
  # Get all teamfamilies
  families = ruil.timetableduty.timetable.team.teammembers.filter(profile=None)

  members = ruil.timetableduty.timetable.team.teammembers.values_list('profile', 'family')

  # Look only in the past {limit} duties
  limit = 2 * len(members)
  # And also include next week
  maxweeks = ruil.timetableduty.event.startdatetime + timedelta(weeks=1)
  duties = ruil.timetableduty.timetable.duties.filter(event__startdatetime__lte=maxweeks).order_by(
    "-event__enddatetime", "-event__startdatetime")[:limit]

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
    if ((ruil.timetableduty.responsible and ruil.timetableduty.responsible.pk is selected_member) \
            or (ruil.timetableduty.responsible_family and ruil.timetableduty.responsible_family.pk is selected_family)) \
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
    'ruil'           : ruil,
    'members'        : profiles,
    'families'       : families,
    'selected_member': selected_member,
    'selected_family': selected_family,
  })


@login_required
@require_POST
def timetable_ruilverzoek_accept(request, id):
  # Get current ruilrequeset
  try:
    ruil = RuilRequest.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Ruilverzoek bestaat niet.')
    return redirect('timetable-list-page')

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(ruil.timetableduty.timetable.team) and not request.user.has_perm(
      'agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=ruil.timetableduty.timetable.team.pk)

  # OK, user is teamleader, let's continue:
  # Sent notification email  to the user
  templateTXT = get_template('email/ruilverzoek_status.txt')
  templateHTML = get_template('email/ruilverzoek_status.html')

  data = Context({
    'resp'    : ruil.profile,
    'status'  : 'geaccepteerd',
    'duty'    : ruil.timetableduty,
    'protocol': 'https',
    'domain'  : get_current_site(None).domain,
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

    try:
      fam = Family.objects.get(pk=resp_id)
    except ObjectDoesNotExist:
      messages.error(request, 'Familie bestaat niet.')
      return redirect('timetable-teamleader-page', id=ruil.timetableduty.timetable.id)

  else:
    try:
      prof = Profile.objects.get(pk=resp_id)
    except ObjectDoesNotExist:
      messages.error(request, 'Profiel bestaat niet.')
      return redirect('timetable-teamleader-page', id=ruil.timetableduty.timetable.id)

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
  try:
    table = Timetable.objects.get(pk=request.POST.get("timetable", ""))
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('timetable-list-page')

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(table.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.pk)

  try:
    event = Event.objects.get(pk=request.POST.get("event", ""))
  except ObjectDoesNotExist:
    messages.error(request, 'Dienst bestaat niet.')
    return redirect('timetable-list-page')

  # Get all responsibles
  resps = request.POST.getlist("responsible[]")

  if len(resps) is 0:
    messages.error(request, "Kies tenminste één persoon of familie.")
    return redirect('timetable-teamleader-page', id=table.id)

  # Create duty for each responsible
  for r in resps:
    # Strip ID
    resp_id = r[1:]

    # Stript type
    if r[0] is "f":
      prof = None

      try:
        fam = Family.objects.get(pk=resp_id)
      except ObjectDoesNotExist:
        messages.error(request, 'Familie bestaat niet.')
        return redirect(reverse('timetable-teamleader-page', kwargs={'id': table.id}) + "#inplannen")

    else:
      try:
        prof = Profile.objects.get(pk=resp_id)
      except ObjectDoesNotExist:
        messages.error(request, 'Profiel bestaat niet.')
        return redirect(reverse('timetable-teamleader-page', kwargs={'id': table.id}) + "#inplannen")

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
  try:
    duty = TimetableDuty.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Taak bestaat niet.')
    return redirect('timetable-list-page')

  if not request.POST.get("timetable", "") or isinstance(request.POST.get("timetable", ""), int):
    table = duty.timetable
  else:
    try:
      table = Timetable.objects.get(pk=request.POST.get("timetable", ""))
    except ObjectDoesNotExist:
      messages.error(request, 'Rooster bestaat niet.')
      return redirect('timetable-list-page')

  # Check if user is teamleader of the new/old timetable's team
  if (not request.profile.teamleader_of(table.team) or not request.profile.teamleader_of(
      duty.timetable.team)) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.team.pk)

  # Get selected user
  resp_id = request.POST.get("responsible")[1:]

  if request.POST.get("responsible")[0] is "f":
    prof = None

    try:
      fam = Family.objects.get(pk=resp_id)
    except ObjectDoesNotExist:
      messages.error(request, 'Familie bestaat niet.')
      return redirect('timetable-detail-page', id=table.id)

  else:
    try:
      prof = Profile.objects.get(pk=resp_id)
    except ObjectDoesNotExist:
      messages.error(request, 'Profiel bestaat niet.')
      return redirect('timetable-detail-page', id=table.id)

    fam = None

  try:
    event = Event.objects.get(pk=request.POST.get("event", ""))
  except ObjectDoesNotExist:
    messages.error(request, 'Dienst bestaat niet.')
    return redirect('timetable-list-page')

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
  try:
    duty = TimetableDuty.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Taak bestaat niet.')
    return redirect('timetable-list-page')

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
  events = Event.objects.filter(startdatetime__gte=datetime.today().date()) \
    .filter(Q(incalendar=True) | Q(incalendar=False, timetable=duty.timetable)) \
    .order_by("startdatetime", "enddatetime", "title")

  # Get all teammembers
  members = duty.timetable.team.teammembers.filter(family=None).order_by('profile__first_name', 'profile__last_name',
                                                                         'profile__birthday')
  # Get all teamfamilies
  families = duty.timetable.team.teammembers.filter(profile=None)

  # Check if current responsible is a teammember
  teammember = TeamMember.objects.filter(team=duty.timetable.team, profile=duty.responsible, family=duty.responsible_family)
  responsible_in_team = len(teammember) > 0

  return render(request, 'teamleader/teamleader_duty_edit.html', {
    'duty'          : duty,
    'table'         : duty.timetable,
    'tables'        : tables,
    'events'        : events,
    'members'       : members,
    'families'      : families,
    'selected_event': duty.event.pk,
    'responsible_in_team': responsible_in_team
  })


@login_required
def timetable_teamleader_duty_delete(request, id):
  try:
    duty = TimetableDuty.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Taak bestaat niet.')
    return redirect('timetable-list-page')

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
#     selected_event = events.exclude(duties__timetable=table.pk).first()
#
#     # Check if object exitsts
#     if selected_event:
#       selected_event = selected_event.pk
#     else:
#       selected_event = 0
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

@login_required
def timetable_import_from_file_index(request, id):
  try:
    timetable = Timetable.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('timetable-detail-page')

  return render(request, 'teampage/csv_upload/upload_page.html', {
    'timetable': timetable
  })

if settings.DEBUG:
  @login_required
  def tools_compare_file_encodings_upload(request):
    if not request.user.has_perm('agenda.change_timetable'):
      return HttpResponse(status=404)

    return render(request, 'tools/file_encodings/file_encoding_upload.html')

  @login_required()
  @require_POST
  def tools_compare_file_encodings_output(request):
    if not request.user.has_perm('agenda.change_timetable'):
      return HttpResponse(status=404)

    # Get file
    upload_files = []
    upload_files.append(request.FILES.get('upload_file0'))
    upload_files.append(request.FILES.get('upload_file1'))
    upload_files.append(request.FILES.get('upload_file2'))
    upload_files.append(request.FILES.get('upload_file3'))

    # Check for file
    if not upload_files:
      messages.error(request, "Er dient een bestand geüpload te worden.")
      return redirect('tools-file-encodings-upload')

    for upload_file in upload_files:
      if not validate_file_extension(upload_file, ['.csv']):
        messages.error(request, "Onjuist bestandsformaat. Het bestand dient een .csv bestand te zijn.");
        return redirect('tools-file-encodings-upload')

    encodings = ['utf-8', 'utf-16', 'latin-1', 'cp720', 'cp1252', 'arabic', 'unicode_escape', 'mac-turkish']
    file_encodings = ['utf-8', 'utf-16', 'latin-1', 'cp720', 'cp1252', 'arabic', 'unicode_escape', 'mac-turkish', 'ISO-8859-1']
    exclude_encoding_pairs = [
      ['utf-8', 'utf-16'],
      ['utf-8', 'latin-1'],
      ['utf-8', 'cp720'],
      ['utf-8', 'cp1252'],
      ['utf-8', 'arabic'],
      ['utf-8', 'unicode_escape'],
      ['utf-8', 'mac-turkish'],
      ['utf-16', 'utf-8'],
      ['utf-16', 'latin-1'],
      ['utf-16', 'cp720'],
      ['utf-16', 'cp1252'],
      ['utf-16', 'arabic'],
      ['utf-16', 'unicode_escape'],
      ['utf-16', 'mac-turkish'],
      ['latin-1', 'utf-16'],
      ['latin-1', 'arabic'],
      ['cp720', 'utf-16'],
      ['cp720', 'arabic'],
      ['cp1252', 'utf-16'],
      ['cp1252', 'arabic'],
      ['arabic', 'utf-8'],
      ['arabic', 'utf-16'],
      ['arabic', 'arabic'],
      ['unicode_escape', 'utf-8'],
      ['unicode_escape', 'utf-16'],
      ['unicode_escape', 'latin-1'],
      ['unicode_escape', 'cp720'],
      ['unicode_escape', 'cp1252'],
      ['unicode_escape', 'arabic'],
      ['unicode_escape', 'mac-turkish'],
      ['mac-turkish', 'utf-16'],
      ['mac-turkish', 'arabic'],
    ]

    table_encodings = []
    for encoding in encodings:
      for decoding in encodings:
        table_encodings.append("%s / %s" % (encoding, decoding))

    files = []
    for upload_file in upload_files:
      # Create a temp file
      # with tempfile.NamedTemporaryFile() as tf:
      file = tempfile.NamedTemporaryFile()

      # Copy the uploaded file to the temp file
      for chunk in upload_file.chunks():
        file.write(chunk)

      # Save contents to file on disk
      file.flush()

      files.append(file)

    # Read file
    table_file_encodings = {}
    for file_encoding in file_encodings:
      encodings_files = {}
      for file in files:
        encoded_file_encodings = []
        encoded_file_exceptions = []
        try:
          with open(file.name, 'r', encoding=file_encoding) as fh:
            lines = csv.DictReader(fh, delimiter=get_delimiter(fh))

            for line in lines:
              # Skip this line if no usefull information is given
              txt = line['Persoon']
              if not (len(txt) and txt[0] == "C"):
                continue

              print("")
              print("ENCODING")
              print("--")
              print(txt)

              for encoding in encodings:
                for decoding in encodings:
                    try:
                      encoded = txt.encode(encoding).decode(decoding)
                      if encoded == "Corné":
                        print("%14s / %14s: %s" % (encoding, decoding, encoded))
                        encoded_file_encodings.append("%s / %s" % (encoding, decoding))
                    except:
                      encoded_file_exceptions.append("%s / %s" % (encoding, decoding))
                      continue
        except:
          pass

        encodings_files[str(file.name)] = [encoded_file_encodings, encoded_file_exceptions]
      # table_file_encodings[file_encoding] = "stuff"
      table_file_encodings[file_encoding] = encodings_files

    table_headers = []
    for encoding in encodings:
      for decoding in encodings:
        if not [encoding, decoding] in exclude_encoding_pairs:
          table_headers.append("%s / %s" % (encoding, decoding))

    for file in files:
      file.close()

    # Return this to a table
    return render(request, 'tools/file_encodings/file_encoding_output.html', {
      'table_headers': table_headers,
      'file_encodings': file_encodings,
      'table_file_encodings': table_file_encodings
    })

@login_required
@require_POST
def timetable_import_from_file_check(request, id):
  try:
    # Get SSL secured timetable pk, and not by URL
    timetable = Timetable.objects.get(pk=request.POST.get("timetable", ""))
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('timetable-detail-page')

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(timetable.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=timetable.pk)

  # Get file
  upload_file = request.FILES.get('upload_file')

  # Check for file
  if not upload_file:
    messages.error(request, "Er dient een bestand geüpload te worden.")
    return redirect('timetable-import-from-file-index', id=timetable.pk)

  if not validate_file_extension(upload_file, ['.csv']):
    messages.error(request, "Onjuist bestandsformaat. Het bestand dient een .csv bestand te zijn.");
    return redirect('timetable-import-from-file-index', id=timetable.pk)

  headers = ['Datum', 'Tijdstip', 'Familie', 'Persoon', 'Extra opmerkingen']

  def get_month_by_name(name):
    months = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']
    return months.index(name.lower()) + 1 if name in months else 0

  families_list = {}
  profiles_list = {}
  # Create a temp file
  with tempfile.NamedTemporaryFile() as tf:
    # Copy the uploaded file to the temp file
    for chunk in upload_file.chunks():
      tf.write(chunk)

    # Save contents to file on disk
    tf.flush()

    # Read file
    with open(tf.name, 'r', encoding="ISO-8859-1") as fh:
      lines = csv.DictReader(fh, delimiter=get_delimiter(fh))

      # Check for needed headers
      missingheaders = list(set(headers) - set(lines.fieldnames))
      if missingheaders:
        if len(missingheaders) > 1:
          messages.error(request, "De kolommen <strong>%s</strong> ontbreken in het bestand." % ', '.join(missingheaders))
        else:
          messages.error(request, "De kolom <strong>%s</strong> ontbreekt in het bestand." % missingheaders[0])
        return redirect('timetable-import-from-file-index', id=timetable.pk)

      # for each line
      date = None
      date_start = None
      date_end = None
      errors_found = 0
      output_lines = []
      line_id = 0
      for line in lines:
        error = {}
        warning = {}

        # Skip this line if no usefull information is given
        if not (line['Familie'] or line['Persoon']):
          continue

        # Make sure the right encoding is used
        for header in headers:
          line[header] = decodeCSV(line[header]).strip()

        # Get date
        # If only month name is given: save this for the next iterations
        # If only nummer is given: get month from saved month ^
        if line['Datum']:
          # Moet nog verder uitgewerkt worden:
          #if int(line['Datum']):
          #  # Only day
          #  day = line['Datum']

          #  if month == 0:
          #    error['datum'] = "Ongeldige datum: er is geen maand bekend."
          #else:
          #  # Parse date to month number
          #  month = get_month_by_name(line['Datum'].strip())

          #  # Validate if it is a month
          #  if month == 0:
          #    # Maybe it is a valid date
          #    try:
          #      date = datetime.strptime(line['Datum'].strip(), "%d-%m-%Y")
          #    except ValueError as e:
          #      error['datum'] = "Ongeldige datum '%s'." % line['Datum']

          try:
            date = datetime.strptime(line['Datum'].strip(), "%d-%m-%Y")
          except ValueError as e:
            error['datum'] = "Ongeldige datum '%s'." % line['Datum']
            date = None
            date_start = None
        # else:
        #   Use date from previous line if it exists, else
        elif date is None:
          error['datum'] = "Onbekende datum."

        # Only process upcoming duties
        if date and date < datetime.now():
          continue

        # Set boundaries for 1 day
        if line['Tijdstip'] and date:
          if line['Tijdstip'] == 'Ochtend':
            # Service time between 8:00 and 13:00
            date_start = date + timedelta(hours=8)
            date_end = date + timedelta(hours=13)
          elif line['Tijdstip'] == 'Middag':
            # Service time between 13:00 and 00:00
            date_start = date + timedelta(hours=13)
            date_end = date + timedelta(hours=24)
          elif line['Tijdstip'] == 'Avond':
            # Service time between 17:00 and 00:00
            date_start = date + timedelta(hours=17)
            date_end = date + timedelta(hours=24)
          elif re.match("^\d?\d:\d\d$", line['Tijdstip']):
            time = line['Tijdstip'].split(':')
            date_start = date + timedelta(hours=int(time[0]), minutes=int(time[1]))
            date_end = None
          elif len(line['Tijdstip']) > 0:
            error['tijdstip'] = "Ongeldige tijdstip '%s'." % line['Tijdstip']
            date_start = None
            date_end = None
        # else:
        #   Use time from previous line if it exists, else
        elif date_start is None:
          #error['tijdstip'] = "Onbekend aanvangs tijdstip."
          date_end = None

        # Search event
        if date_start:
          if date_end:
            event = Event.objects.filter(startdatetime__gte=date_start, enddatetime__lt=date_end)
          else:
            event = Event.objects.filter(startdatetime=date_start)

          if len(event) > 1:
            error['event'] = "Meerdere diensten gevonden op dit tijdstip."
            event = None
          elif event is None or len(event) == 0:
            error['event'] = "Geen diensten gevonden voor dit tijdstip."
          else:
            event = event.first()
        else:
          event = None

        # Check if other duties already exists for this service
        duty = TimetableDuty.objects.filter(timetable=timetable, event=event)
        warning_duplicate = "Er zijn reeds andere inroosteringen voor deze dienst." if duty else None

        # Get description/comment
        comments = line['Extra opmerkingen']

        # Save whole in dict
        main_line = {}
        main_line['datum'] = date if date else line['Datum']
        main_line['tijdstip'] = line['Tijdstip']
        main_line['event'] = event
        main_line['comments'] = comments

        for key, val in error.items():
          error_name = 'error_%s' % key
          main_line[error_name] = val

        for key, val in warning.items():
          warning_name = 'warning_%s' % key
          main_line[warning_name] = val

        # Split families into array
        if line['Familie']:
          for familie in line['Familie'].split('/'):
            tmp_error = {}
            tmp_warning = {}
            line_id += 1

            # Validations and filters
            familie = familie.strip()

            family_name = re.sub(r"^Fam\.\s?", '', familie.strip(), flags=re.IGNORECASE).strip().split(' ')
            lastname = family_name[-1]
            family = Family.objects.filter(lastname=lastname)

            # Filter family list even further based on the name (prefix and initials)
            if len(family) > 1 and len(family_name) > 1:
                # Make search query more strict
                if '.' in family_name[0]:
                  families_found = []
                  for fam in family:
                    if fam.householder() and fam.householder().first().initials == family_name[0]:
                      families_found.append(fam.pk)

                  family = family.filter(pk__in=families_found)

                  if len(family_name) > 2:
                    family = family.filter(prefix="%s%s%s" % (family_name[-3], (' ' if len(family_name) > 4 else ''), family_name[-2]))  # Verkrijg een-na-laastse, to leave room for more initals

                else:
                  families = family.filter(prefix=family_name[0])
                  # If still multiple families are found, orraait
                  # but if suddenly no families are found, use the old family list to fire the 'select one of multiple families' warning
                  if len(families):
                    family = families

            if len(family) > 1:
              # Try to be smart and select the familie which is in the team
              teammembers = TeamMember.objects.filter(team=timetable.team, family__in=family)

              # If one is found
              if len(teammembers) == 1:
                # Set the family
                family = teammembers.first().family
              else:
                tmp_warning['familie'] = "Meerdere families gevonden voor '%s'." % lastname
                families_list[line_id] = family
                family = None

            elif family is None or len(family) == 0:
              tmp_error['familie'] = "Geen families gevonden voor '%s'." % lastname
            else:
              family = family.first()

              # Check if familie is in team
              try:
                TeamMember.objects.get(team=timetable.team, family=family)
              except ObjectDoesNotExist:
                tmp_warning['familie'] = "Familie is geen lid van het team."

            # Check if the timetable duty already exists
            duty = TimetableDuty.objects.filter(timetable=timetable, event=event, responsible=None, responsible_family=family)
            duplicate_found = duty.first().id if duty else False
            if duplicate_found:
              tmp_warning['duplicate'] = "Deze inroostering bestaat al."
            elif warning_duplicate:
              tmp_warning['duplicate'] = warning_duplicate

            # Save whole in the dict
            temp_line = {}
            temp_line['id'] = line_id
            temp_line['familie'] = family if family else familie
            temp_line['persoon'] = None
            temp_line['errors_found'] = len(error) + len(tmp_error)
            temp_line['warnings_found'] = len(warning) + len(tmp_warning)
            temp_line['duplicate_found'] = duplicate_found

            for key,val in tmp_error.items():
              error_name = 'error_%s' % key
              temp_line[error_name] = val

            for key,val in tmp_warning.items():
              warning_name = 'warning_%s' % key
              temp_line[warning_name] = val

            # Count total invalid lines
            if len(error) or len(tmp_error):
              errors_found += 1

            temp_line.update(main_line)
            output_lines.append(temp_line)

        # Split persons into array
        if line['Persoon']:
          for persoon in line['Persoon'].split('/'):
            tmp_error = {}
            tmp_warning = {}
            line_id += 1

            # Validations and filters
            persoon = persoon.strip()

            # Create first and possible last name
            persoon_names = persoon.split(' ')
            firstname = persoon_names[0].strip()

            if len(persoon_names) > 1:
              lastname = persoon_names[-1].strip()
              profile = Profile.objects.filter(first_name=firstname, last_name=lastname)
            else:
              lastname = None
              profile = Profile.objects.filter(first_name=firstname)

            if len(profile) > 1:
              # Try to be smart and select the person who is in the team
              teammembers = TeamMember.objects.filter(team=timetable.team, profile__in=profile)

              # If one is found
              if len(teammembers) == 1:
                # Set the profile
                profile = teammembers.first().profile
              else:
                tmp_warning['persoon'] = "Meerdere personen gevonden voor '%s'." % persoon
                profiles_list[line_id] = profile
                profile = None

            elif profile is None or len(profile) == 0:
              tmp_error['persoon'] = "Geen persoon gevonden voor '%s'." % persoon
            else:
              profile = profile.first()

              # Check if profile is in team
              try:
                TeamMember.objects.get(team=timetable.team, profile=profile)
              except ObjectDoesNotExist:
                tmp_warning['persoon'] = "Persoon is geen lid van het team."

            # Check if the timetable duty already exists
            duty = TimetableDuty.objects.filter(timetable=timetable, event=event, responsible=profile, responsible_family=None)
            duplicate_found = duty.first().id if duty else False
            if duplicate_found:
              tmp_warning['duplicate'] = "Deze inroostering bestaat al."
            elif warning_duplicate:
              tmp_warning['duplicate'] = warning_duplicate

            # Save whole as object
            temp_line = {}
            temp_line['id'] = line_id
            temp_line['familie'] = None
            temp_line['persoon'] = profile if profile else persoon
            temp_line['errors_found'] = len(error) + len(tmp_error)
            temp_line['warnings_found'] = len(warning) + len(tmp_warning)
            temp_line['duplicate_found'] = duplicate_found

            for key, val in tmp_error.items():
              error_name = 'error_%s' % key
              temp_line[error_name] = val

            for key, val in tmp_warning.items():
              warning_name = 'warning_%s' % key
              temp_line[warning_name] = val

            # Count total invalid lines
            if len(error) or len(tmp_error):
              errors_found += 1

            temp_line.update(main_line)
            output_lines.append(temp_line)

  if output_lines:
    if errors_found:
      messages.error(request, "Er zijn %d regels met een fout. Deze regels kunnen niet geïmporteerd worden." % errors_found)
    else:
      messages.success(request, "Er zijn geen fouten gevonden!")

  # Create a json representation of the lines which have no errors
  valid_lines = {}
  for output_line in output_lines:
    if output_line['errors_found'] == 0:
      line = {
        'datum':    output_line['datum'],
        'tijdstip': output_line['tijdstip'],
        'event':    output_line['event'].pk if output_line['event'] else '',
        'familie':  output_line['familie'].pk if isinstance(output_line['familie'], Family) else '',
        'persoon':  output_line['persoon'].pk if isinstance(output_line['persoon'], Profile) else '',
        'comments': output_line['comments']
      }
      valid_lines[output_line['id']] = line
  json_valid_lines = json.dumps(valid_lines, default=str)

  return render(request, 'teampage/csv_upload/check_page.html', {
    'timetable':        timetable,
    'output_lines':     output_lines,
    'json_valid_lines': json_valid_lines,
    'families_list':    families_list,
    'profiles_list':    profiles_list
  })

@login_required
@require_POST
def timetable_import_from_file_save(request, id):
  DEBUG_CSVROOSTERIMPORT = True

  try:
    # Get SSL secured timetable pk, and not by URL
    timetable = Timetable.objects.get(pk=request.POST.get("timetable", ""))
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('timetable-detail-page')

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(timetable.team) and not request.user.has_perm('agenda.change_timetable'):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=timetable.pk)

  # Retrieve data
  json_valid_lines = request.POST.get("json_valid_lines", None)
  json_selected_lines = request.POST.get("json_selected_lines", None)
  json_selected_responsibles = request.POST.get("json_selected_responsibles", None)

  # Process data
  if not (json_valid_lines and json_selected_lines):
    messages.error(request, "Geen data doorgekregen.")
    return redirect('timetable-import-from-file-index', id=timetable.pk)

  # Parse the json
  valid_lines = json.loads(json_valid_lines if len(json_valid_lines) else "[]")
  selected_lines = json.loads(json_selected_lines if len(json_selected_lines) else "[]")
  selected_responsibles = json.loads(json_selected_responsibles if len(json_selected_responsibles) else "[]")

  # Process data
  if len(selected_lines) == 0:
    messages.warning(request, "Er is niets geselecteerd om te importeren.")
    return redirect('timetable-teamleader-page', id=timetable.pk)

  for selected_line in selected_lines:
    line = valid_lines[selected_line]

    # Get the valid Events object
    try:
      event = Event.objects.get(pk=line['event'])
    except ObjectDoesNotExist:
      messages.error(request, "Onjuiste dienst voor de inroostering op %s, %s." % (line['datum'], line['tijdstip']))
      continue

    # Get the valid Family or Profile object
    family = None
    profile = None
    # First look if there was a custom one selected
    if not(line['familie'] or line['persoon']) and selected_responsibles[selected_line]:
      responsible = selected_responsibles[selected_line].split('_')
      if responsible[0] == 'familie':
        line['familie'] = responsible[1]
      elif responsible[0] == 'persoon':
        line['persoon'] = responsible[1]

    # Now get the right guy
    if line['familie']:
      try:
        family = Family.objects.get(pk=line['familie'])
      except ObjectDoesNotExist:
        messages.error(request, "Onjuiste familie voor de inroostering op %s, %s." % (line['datum'], line['tijdstip']))
        continue
    elif line['persoon']:
      try:
        profile = Profile.objects.get(pk=line['persoon'])
      except ObjectDoesNotExist:
        messages.error(request, "Onjuiste persoon voor de inroostering op %s, %s." % (line['datum'], line['tijdstip']))
        continue
    else:
      messages.error(request, "Geen familie of persoon doorgekregen voor de inroostering op %s, %s." % (line['datum'], line['tijdstip']))
      continue

    # Check if duty already exists
    duty = TimetableDuty.objects.filter(timetable=timetable, event=event, responsible=profile, responsible_family=family).first()
    if duty:
      # Update duty
      duty.comments = line['comments']
      if DEBUG_CSVROOSTERIMPORT:
        messages.success(request, "De inroostering van %s voor '%s' is bijgewerkt." % (duty.resp_name(), event))
      else:
        duty.save()

    else:
      # Create the new duty
      if DEBUG_CSVROOSTERIMPORT:
        messages.success(request, "%s is ingepland voor '%s'." % (family if family else profile, event))
      else:
        duty = TimetableDuty.objects.create(
         timetable=timetable,
         event=event,
         responsible_family=family,
         responsible=profile,
         comments=line['comments']
        )

        messages.success(request, "%s is ingepland voor '%s'." % (duty.resp_name(), event))

  return redirect('timetable-teamleader-page', id=timetable.pk)


# Calendar
@login_required
def calendar(request):
  return render(request, 'calendar.html')


# When editting URLs, pay attention for the Ajax call in app.jsx -> window.timetableMain()

@login_required
@permission_required('agenda.add_service', raise_exception=True)
def services_admin(request):
  ## set default date to next sunday without a service
  # Get today's date
  today_date = datetime.today().date()

  # Get last sunday service, from today and on
  last = Service.objects.filter(startdatetime__week_day=1, startdatetime__gte=today_date).order_by('-startdatetime').first()

  # Add one week
  if last:
    startdatetime = last.startdatetime + timedelta(weeks=1)
  else:
    # Get next upcoming sunday
    startdatetime = today_date + timedelta(days=-today_date.weekday() - 1, weeks=1)

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

  try:
    timetable = Timetable.objects.get(title="Diensten")
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster \'Diensten\' bestaat niet.')
    return redirect('services-admin')

  Service.objects.create(
    startdatetime=startdate,
    enddatetime=enddate,
    owner=request.profile,
    title=request.POST.get("title1", "").strip(),
    timetable=timetable,
    minister=request.POST.get("minister1", "").strip(),
    theme=request.POST.get("theme1", "").strip(),
    comments=request.POST.get("comments1", "").strip(),
    description=request.POST.get("description1", "").strip(),
    incalendar=True,
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

    try:
      timetable = Timetable.objects.get(title="Diensten")
    except ObjectDoesNotExist:
      messages.error(request, 'Rooster \'Diensten\' bestaat niet.')
      return redirect('services-admin')

    Service.objects.create(
      startdatetime=startdate,
      enddatetime=enddate,
      owner=request.profile,
      title=request.POST.get("title2", "").strip(),
      timetable=timetable,
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
  try:
    service = Service.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Dienst bestaat niet.')
    return redirect('services-admin')

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
  try:
    service = Service.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Dienst bestaat niet.')
    return redirect('services-admin')

  return render(request, 'services/edit.html', {
    'service': service,
  })


@login_required
@permission_required('agenda.delete_service', raise_exception=True)
def services_admin_delete(request, id):
  try:
    Service.objects.get(pk=id).delete()
  except ObjectDoesNotExist:
    messages.error(request, 'Dienst bestaat niet.')
    return redirect('services-admin')

  # Delete all duties of this service
  TimetableDuty.objects.filter(event__pk=id).delete()

  messages.success(request, "Dienst is verwijderd.")

  return redirect('services-admin')


# Team pages

@login_required
def teampage_control_members(request, id):
  try:
    team = Team.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Team bestaat niet.')
    return redirect('team-list-page')

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=id)

  members = team.teammembers.order_by('family__lastname', 'profile__first_name')

  roles = TeamMemberRole.objects.active().order_by('name')

  # Render that stuff!
  return render(request, 'teampage/teampage_control_members.html', {
    'team'         : team,
    'members'      : members,
    'roles'        : roles,
    'selected_role': 'LID',
  })


@login_required
@require_POST
def teampage_control_members_add(request):
  team_id = request.POST.get("team", "")
  profile = request.POST.get("profile", "0")
  family = request.POST.get("family", "0")


  try:
    team = Team.objects.get(pk=team_id)
  except ObjectDoesNotExist:
    messages.error(request, 'Team bestaat niet.')
    return redirect('team-list-page')

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team.pk) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=team.pk)

  # Check if profile is valid
  if family is "0" and TeamMember.objects.filter(team_id=team.pk, profile_id=profile).exists():
    messages.error(request, "Het gekozen lid maakt al deel uit van dit team.")
    return redirect('teampage-control-members', id=team.pk)

  # Check if profile is valid
  if profile is "0" and TeamMember.objects.filter(team_id=team.pk, family_id=family).exists():
    messages.error(request, "De gekozen familie maakt al deel uit van dit team.")
    return redirect('teampage-control-members', id=team.pk)

  if Profile.objects.filter(pk=profile).exists():
    try:
      prof = Profile.objects.get(pk=profile)
    except ObjectDoesNotExist:
      messages.error(request, 'Profiel bestaat niet.')
      return redirect('teampage-control-members', id=team.pk)

    fam = None

  elif Family.objects.filter(pk=family).exists():
    prof = None

    try:
      fam = Family.objects.get(pk=family)
    except ObjectDoesNotExist:
      messages.error(request, 'Familie bestaat niet.')
      return redirect('teampage-control-members', id=team.pk)

  else:
    messages.error(request, "Er is geen (geldig) lid/familie gekozen om toe te voegen.")
    return redirect('teampage-control-members', id=team.pk)

  try:
    role = TeamMemberRole.objects.get(pk=request.POST.get("role", ""))
  except ObjectDoesNotExist:
    messages.error(request, 'Teamrol bestaat niet.')
    return redirect('teampage-control-members', id=team.pk)

  TeamMember.objects.create(
    team=team,
    profile=prof,
    family=fam,
    role=role,
    is_admin=True if request.POST.get("is_admin", False) else False
  )

  messages.success(request, "Het nieuwe teamlid is toegevoegd.")

  return redirect('teampage-control-members', id=team.pk)


@login_required
@require_POST
def teampage_control_members_edit_save(request, id):
  try:
    member = TeamMember.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Teamlid bestaat niet.')
    return redirect('team-list-page')

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(member.team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=member.team.pk)

  try:
    role = TeamMemberRole.objects.get(pk=request.POST.get("role", ""))
  except ObjectDoesNotExist:
    messages.error(request, 'Teamrol bestaat niet.')
    return redirect('teampage-control-members', id=team.pk)

  member.role = role
  member.is_admin = True if request.POST.get("is_admin", False) else False
  member.save()

  messages.success(request, "De wijzigingen zijn opgeslagen.")

  return redirect('teampage-control-members', id=member.team.pk)


@login_required
def teampage_control_members_edit(request, id):
  try:
    member = TeamMember.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Teamlid bestaat niet.')
    return redirect('team-list-page')

  roles = TeamMemberRole.objects.active().order_by('name')

  # Render that stuff!
  return render(request, 'teampage/teampage_control_members_edit.html', {
    'team'  : member.team,
    'member': member,
    'roles' : roles,
  })


@login_required
def teampage_control_members_delete(request, id):
  try:
    member = TeamMember.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Teamlid bestaat niet.')
    return redirect('team-list-page')

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
  try:
    team = Team.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Team bestaat niet.')
    return redirect('team-list-page')

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=id)

  tables = team.timetables

  return render(request, 'teampage/control_timetables.html', {
    'team'        : team,
    'tables'      : tables,
    'random_color': '{:06x}'.format(random.randint(0, 0xffffff)),
  })


@login_required
@require_POST
def teampage_control_timetables_add(request):
  try:
    team = Team.objects.get(pk=request.POST.get("team", ""))
  except ObjectDoesNotExist:
    messages.error(request, 'Team bestaat niet.')
    return redirect('team-list-page')

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=team.pk)

  if request.POST.get("color", "")[0] is "#":
    color = request.POST.get("color", "")[1:]
  else:
    color = request.POST.get("color", "")

  if len(team.timetables.all()) and not request.user.has_perm('agenda.change_team'):
    messages.error(request,
                   "Je hebt al een rooster voor dit team toegevoegd. Het limiet staat op één rooster per team.")
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
  try:
    table = Timetable.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('team-list-page')

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
  try:
    table = Timetable.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('team-list-page')

  return render(request, 'teampage/control_timetables_edit.html', {
    'table': table,
  })


@login_required
@require_POST
def teampage_control_timetables_edit_save(request, id):
  try:
    table = Timetable.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('team-list-page')

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
  try:
    team = Team.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Team bestaat niet.')
    return redirect('team-list-page')

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
  remindermail = re.sub('(<p>&nbsp;</p>[\n\r]*)*$', '', remindermail, flags=re.IGNORECASE)
  # Remove begin
  remindermail = re.sub('^(<p>&nbsp;</p>[\n\r]*)*', '', remindermail, flags=re.IGNORECASE)

  description = request.POST.get("description", "").strip()
  # Remove end
  description = re.sub('(<p>&nbsp;</p>[\n\r]*)*$', '', description, flags=re.IGNORECASE)
  # Remove begin
  description = re.sub('^(<p>&nbsp;</p>[\n\r]*)*', '', description, flags=re.IGNORECASE)

  team.name = request.POST.get("name", "").strip()
  team.email = email
  team.description = description.strip()
  team.remindermail = remindermail.strip()
  team.save()

  messages.success(request, "De instellingen zijn opgeslagen.")

  return redirect('teampage', id=team.pk)


@login_required
def teampage_control_edit(request, id):
  try:
    team = Team.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Team bestaat niet.')
    return redirect('team-list-page')

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
  try:
    team = Team.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Team bestaat niet.')
    return redirect('team-list-page')

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
    'team'             : team,
    'is_admin'         : request.profile.teamleader_of(team),
    'teammember'       : teammember,
    'teammember_family': teammember_family,
    'members'          : members,
    'tables'           : tables,
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
  try:
    team = Team.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Team bestaat niet.')
    return redirect('team-list-page')

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
    try:
      ef = EventFile.objects.get(pk=int(id))
    except ObjectDoesNotExist:
      messages.error(request, 'Bestand bestaat niet.')

    selected_service = ef.event.pk

  else:
    if services.filter(files=None).exists():
      selected_service = services.filter(files=None).first()
    else:
      selected_service = services.first()

    # Check if object exists
    if selected_service:
      selected_service = selected_service.pk
    else:
      selected_service = 0

  maxweeks = datetime.today().date() - timedelta(weeks=2)
  efs = EventFile.objects.filter(event__startdatetime__gte=maxweeks) \
    .order_by("-event__startdatetime", "-event__enddatetime", "event__title", "event__pk", "title")

  return render(request, 'services/files_add.html', {
    'recent_services' : recent_services,
    'services'        : services,
    'selected_service': selected_service,
    'ef'              : ef,
    'efs'             : efs,
    'maxweeks'        : maxweeks
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
  try:
    ef = EventFile.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Bestand bestaat niet.')
    return redirect('services-files-admin')

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
  try:
    ef = EventFile.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Bestand bestaat niet.')
    return redirect('services-files-admin')

  ef.delete()

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
    startdatetime = today + timedelta(days=-today.weekday() - 1, weeks=1)

  return render(request, 'services/list.html', {
    'startdatetime': startdatetime,
  })


@login_required
def services_single(request, id):
  try:
    service = Service.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Dienst bestaat niet.')
    return redirect('services-page')

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


@login_required
@permission_required('agenda.add_event', raise_exception=True)
def events_admin(request):
  # Get today
  startdatetime = datetime.today()

  # Round to nearest (half) hour
  startdatetime = startdatetime + timedelta(minutes=(30 - startdatetime.minute % 30))
  enddatetime = startdatetime + timedelta(hours=1)

  # Get teams the profile belongs to
  if request.user.has_perm('agenda.add_timetable'):
    timetables = Timetable.objects.all()
  else:
    memberships = TeamMember.objects \
      .prefetch_related("team") \
      .filter(Q(profile=request.profile) | Q(family=request.profile.family)) \
      .filter(is_admin=True) \
      .order_by('team__name')

    teams = memberships.values_list('team', flat=True)

    # Remove double memberships (like profile AND family), filter on (i.)team
    teams = uniqify(teams)

    # Get timetables
    timetables = Timetable.objects.filter(team__in=teams)

  # Get all custom events
  maxweeks = datetime.today().date() - timedelta(weeks=4)
  services = Service.objects.filter(startdatetime__gte=maxweeks).values_list('pk', flat=True)
  events = Event.objects.filter(startdatetime__gte=maxweeks) \
    .exclude(pk__in=services) \
    .order_by("startdatetime", "enddatetime", "title")

  return render(request, 'events/admin.html', {
    'startdatetime': startdatetime,
    'enddatetime': enddatetime,
    'timetables': timetables,
    'events': events
  })


@login_required
@require_POST
@permission_required('agenda.add_event', raise_exception=True)
def events_admin_add(request):
  # Get datetimes
  startdatetime = "%s %s:00" % (str(request.POST.get("startdate")), str(request.POST.get("starttime")))
  enddatetime = "%s %s:00" % (str(request.POST.get("enddate")), str(request.POST.get("endtime")))

  try:
    startdatetime = datetime.strptime(startdatetime, '%d-%m-%Y %H:%M:%S')
    enddatetime = datetime.strptime(enddatetime, '%d-%m-%Y %H:%M:%S')
  except ValueError:
    messages.error(request, 'Het formaat van de ingevulde datum en/of tijdstip klopt niet.')
    return redirect('events-admin')

  timetable = int(request.POST.get("timetable"))
  if timetable < 1:
    messages.error(request, 'Selecteer een rooster.')
    return redirect('events-admin')


  try:
    timetable = Timetable.objects.get(pk=timetable)
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('events-admin')

  Event.objects.create(
    startdatetime=startdatetime,
    enddatetime=enddatetime,
    owner=request.profile,
    title=request.POST.get("title", "").strip(),
    description=request.POST.get("description", "").strip(),
    timetable=timetable,
    incalendar=True if request.POST.get("incalendar") else False,
  )

  messages.success(request, "Gebeurtenis is toegevoegd.")

  return redirect('events-admin')


@login_required
@require_POST
@permission_required('agenda.change_event', raise_exception=True)
def events_admin_edit_save(request, id):
  try:
    event = Event.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Event bestaat niet.')
    return redirect('events-admin')

  # Get datetimes
  startdatetime = "%s %s:00" % (str(request.POST.get("startdate", event.startdatetime.date())), str(request.POST.get("starttime", event.startdatetime.time())))
  enddatetime = "%s %s:00" % (str(request.POST.get("enddate", event.enddatetime.date())), str(request.POST.get("endtime", event.enddatetime.time())))

  try:
    startdatetime = datetime.strptime(startdatetime, '%d-%m-%Y %H:%M:%S')
    enddatetime = datetime.strptime(enddatetime, '%d-%m-%Y %H:%M:%S')
  except ValueError:
    messages.error(request, 'Het formaat van de ingevulde datum en/of tijdstip klopt niet.')
    return redirect('events-admin')

  timetable = int(request.POST.get("timetable", event.timetable.pk))
  if timetable < 1:
    messages.error(request, 'Selecteer een rooster.')
    return redirect('events-admin')

  try:
    timetable = Timetable.objects.get(pk=timetable)
  except ObjectDoesNotExist:
    messages.error(request, 'Rooster bestaat niet.')
    return redirect('events-admin')

  event.startdatetime = startdatetime
  event.enddatetime = enddatetime
  event.title = request.POST.get("title", "").strip()
  event.description = request.POST.get("description", "").strip()
  event.timetable = timetable
  event.incalendar = True if request.POST.get("incalendar") else False

  event.save()

  messages.success(request, "Gebeurtenis is opgeslagen.")

  return redirect('events-admin')


@login_required
@permission_required('agenda.change_event', raise_exception=True)
def events_admin_edit(request, id):
  try:
    event = Event.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Event bestaat niet.')
    return redirect('events-admin')

  # Get teams the profile belongs to
  memberships = TeamMember.objects \
    .prefetch_related("team") \
    .filter(Q(profile=request.profile) | Q(family=request.profile.family)) \
    .filter(is_admin=True) \
    .order_by('team__name')

  teams = memberships.values_list('team', flat=True)

  # Remove double memberships (like profile AND family), filter on (i.)team
  teams = uniqify(teams)

  # Get timetables
  timetables = Timetable.objects.filter(team__in=teams)

  return render(request, 'events/edit.html', {
    'event': event,
    'timetables': timetables,
  })


@login_required
#@require_POST
@permission_required('agenda.delete_event', raise_exception=True)
def events_admin_delete(request, id):
  try:
    Event.objects.get(pk=id).delete()
  except ObjectDoesNotExist:
    messages.error(request, 'Event bestaat niet of kon niet verwijderd worden.')
    return redirect('events-admin')

  # Delete all duties of this service
  TimetableDuty.objects.filter(event__pk=id).delete()

  messages.success(request, "Event is verwijderd.")

  return redirect('events-admin')


@login_required
def events_single(request, id):
  try:
    event = Event.objects.get(pk=id)
  except ObjectDoesNotExist:
    messages.error(request, 'Event bestaat niet.')
    return redirect('dashboard')

  return render(request, 'events/single.html', {
    'event': event,
  })


urls = [
  url(r'^roosters/ruilverzoek/new/(?P<id>\d+)/$', timetable_ruilen, name='timetable-ruilen'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/intrekken/$', timetable_undo_ruilen, name='timetable-undo-ruilen'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/afwijzen/$', timetable_undo_ruilen_teamleader,
      name='timetable-undo-ruilen-teamleader'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/accept/$', timetable_ruilverzoek_accept, name='timetable-ruilverzoek-accept'),
  url(r'^roosters/ruilverzoek/(?P<id>\d+)/$', timetable_ruilverzoek, name='timetable-ruilverzoek'),

  url(r'^roosters/teamleider/duty/add/$', timetable_teamleader_duty_add, name='timetable-teamleader-duty-add'),
  url(r'^roosters/teamleider/duty/(?P<id>\d+)/edit/save/$', timetable_teamleader_duty_edit_save,
      name='timetable-teamleader-duty-edit-save'),
  url(r'^roosters/teamleider/duty/(?P<id>\d+)/edit/$', timetable_teamleader_duty_edit,
      name='timetable-teamleader-duty-edit'),
  url(r'^roosters/teamleider/duty/(?P<id>\d+)/delete/$', timetable_teamleader_duty_delete,
      name='timetable-teamleader-duty-delete'),

  url(r'^roosters/(?P<id>\d+)/teamleider/importeren/$', timetable_import_from_file_index,
      name='timetable-import-from-file-index'),
  url(r'^roosters/(?P<id>\d+)/teamleider/importeren/check/$', timetable_import_from_file_check,
     name='timetable-import-from-file-check'),
  url(r'^roosters/(?P<id>\d+)/teamleider/importeren/save/$', timetable_import_from_file_save,
      name='timetable-import-from-file-save'),

  url(r'^roosters/(?P<id>\d+)/teamleider/$', timetable_teamleader, name='timetable-teamleader-page'),

  url(r'^roosters/(?P<id>\d+)/$', timetables, name='timetable-detail-page'),

  url(r'^roosters$', RedirectView.as_view(url='roosters/', permanent=True)),
  url(r'^roosters/$', timetables, name='timetable-list-page'),

  url(r'^kalender$', RedirectView.as_view(url='kalender/', permanent=True)),
  url(r'^kalender/$', calendar, name='calendar-page'),

  url(r'^team/leden/add/$', teampage_control_members_add, name='teampage-control-members-add'),
  url(r'^team/leden/(?P<id>\d+)/edit/save/$', teampage_control_members_edit_save,
      name='teampage-control-members-edit-save'),
  url(r'^team/leden/(?P<id>\d+)/edit/$', teampage_control_members_edit, name='teampage-control-members-edit'),
  url(r'^team/leden/(?P<id>\d+)/delete/$', teampage_control_members_delete, name='teampage-control-members-delete'),
  url(r'^team/(?P<id>\d+)/leden/$', teampage_control_members, name='teampage-control-members'),

  url(r'^team/roosters/add/$', teampage_control_timetables_add, name='teampage-control-timetables-add'),
  url(r'^team/roosters/(?P<id>\d+)/delete/$', teampage_control_timetables_delete,
      name='teampage-control-timetables-delete'),
  url(r'^team/roosters/(?P<id>\d+)/edit/save/$', teampage_control_timetables_edit_save,
      name='teampage-control-timetables-edit-save'),
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

  url(r'^roosters/events/beheren/toevoegen/$', events_admin_add, name='events-admin-add'),
  url(r'^roosters/events/beheren/(?P<id>\d+)/edit/save/$', events_admin_edit_save, name='events-admin-edit-save'),
  url(r'^roosters/events/beheren/(?P<id>\d+)/edit/$', events_admin_edit, name='events-admin-edit'),
  url(r'^roosters/events/beheren/(?P<id>\d+)/delete/$', events_admin_delete, name='events-admin-delete'),
  url(r'^roosters/events/beheren/$', events_admin, name='events-admin'),

  url(r'^roosters/diensten/$', services_page, name='services-page'),
  url(r'^roosters/diensten/(?P<id>\d+)/$', services_single, name='services-single'),
  url(r'^roosters/events/(?P<id>\d+)/$', events_single, name='events-single'),

  url(r'^roosters/diensten/bestanden/beheren/(?P<id>\d+)/delete/$', services_files_admin_delete,
      name='services-files-admin-delete'),
  url(r'^roosters/diensten/bestanden/beheren/(?P<id>\d+)/edit/save/$', services_files_admin_edit_save,
      name='services-files-admin-edit-save'),
  url(r'^roosters/diensten/bestanden/beheren/(?P<id>\d+)/edit/$', services_files_admin,
      name='services-files-admin-edit'),
  url(r'^roosters/diensten/bestanden/beheren/toevoegen/$', services_files_admin_add, name='services-files-admin-add'),
  url(r'^roosters/diensten/bestanden/beheren/$', services_files_admin, name='services-files-admin'),
]

if settings.DEBUG:
  urls = urls + [
    url(r'^tools/fileencoding/output', tools_compare_file_encodings_output,
      name='tools-file-encodings-output'),
    url(r'^tools/fileencoding/upload', tools_compare_file_encodings_upload,
      name='tools-file-encodings-upload'),
  ]
