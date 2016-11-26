from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import *
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf.urls import include, url
from django.conf import settings
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import random
from .models import *
from base.models import Profile
from .forms import *

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
    # Redirect to first public page
    return redirect('timetable-detail-page', id=req_id)

  # Send notification email to the user
  template = get_template('email/ruilverzoek_status.txt')

  data = Context({
    'name': req.profile.name(),
    'status': 'afgewezen',
    'timetable': req.timetableduty.timetable.title,
    'duty': req.timetableduty,
    'sendtime': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
  })

  message = template.render(data)

  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [ req.profile.email ]
  send_mail("Ruilverzoek afgewezen", message, from_email, to_emails)

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
    comments=request.POST.get("comments", "").strip()
  )

  # inform team leader
  template = get_template('email/ruilverzoek.txt')

  if request.POST.get("comments", ""):
    comments = "Met de volgende redenen: \n %s" % request.POST.get("comments", "").strip()
  else:
    comments = "Er is geen reden gegeven."

  data = Context({
    'name': request.profile.name(),
    'timetable': duty.timetable.title,
    'duty': duty,
    'comments': comments,
    'sendtime': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
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
    .order_by("startdatetime", "enddatetime", "title")

  # set default selection to event without duty (belonging to this timetable)
  if events.exclude(duties__timetable=table.pk).exists():
    selected_event = events.exclude(duties__timetable=table.pk).first().pk
  else:
    selected_event = 0

  # Get all teammembers
  members = table.team.teammembers

  # set default selection to member which is last scheduled
  duties = table.duties.filter(event__enddatetime__gte=datetime.today().date()).order_by("-event__enddatetime",
                                                                                         "-event__startdatetime")
  if duties.exists():
    # get only users that are still teammembers
    responsibles = duties.filter(responsible__in=members.values_list('profile', flat=True)).values_list('responsible',
                                                                                                        flat=True)

    unique_responsibles = uniqify(responsibles)

    # Add also the members who aren't scheduled for any duty yet
    b = members.values_list('profile', flat=True)
    all_responsibles = uniqify(unique_responsibles + uniqify(b))

    selected_member = all_responsibles[-1]
  else:
    selected_member = 0

  # Render that stuff!
  return render(request, 'teamleader/teamleader.html', {
    'table': table,
    'ruils': ruils,
    'team': table.team,
    'events': events,
    'members': members,
    'selected_event': selected_event,
    'selected_member': selected_member,
  })

@login_required
def timetable_ruilverzoek(request, id):
  # Get current ruilrequeset
  ruil = RuilRequest.objects.get(pk=id)

  # Check if user is teamleader of this timetable's team
  if not request.profile.teamleader_of(ruil.timetableduty.timetable.team):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=ruil.timetableduty.timetable.team.pk)

  # OK, user is teamleader, let's continue:

  # Get all teammembers
  members = ruil.timetableduty.timetable.team.teammembers.all()

  # set default selection to member which is last scheduled
  duties = ruil.timetableduty.timetable.duties.filter(event__enddatetime__gte=datetime.today().date()).order_by("-event__enddatetime", "-event__startdatetime")
  if duties.exists():
    responsibles = duties.values_list('responsible', flat=True)
    unique_responsibles = uniqify(responsibles)

    # Add also the members who aren't scheduled for any duty yet
    b = members.values_list('profile', flat=True)
    all_responsibles = uniqify(unique_responsibles + uniqify(b))

    if len(all_responsibles) > 1:
      all_responsibles.remove(ruil.timetableduty.responsible.pk)

    selected_member = all_responsibles[-1]
  else:
    selected_member = 0

  # Render that stuff!
  return render(request, 'teamleader/ruilverzoek.html', {
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
    # Redirect to first public page
    return redirect('timetable-detail-page', id=ruil.timetableduty.timetable.team.pk)

  # OK, user is teamleader, let's continue:
  # Sent notification email to the user
  template = get_template('email/ruilverzoek_status.txt')

  data = Context({
    'name': ruil.profile.name(),
    'status': 'geaccepteerd',
    'timetable': ruil.timetableduty.timetable.title,
    'duty': ruil.timetableduty,
    'sendtime': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
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
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.team.pk)

  event = Event.objects.get(pk=request.POST.get("event", ""))
  responsible = Profile.objects.get(pk=request.POST.get("responsible", ""))

  # Create new duty
  TimetableDuty.objects.create(
    timetable=table,
    event=event,
    responsible=responsible,
    comments=request.POST.get("comments", "").strip()
  )

  messages.success(request, "%s is ingepland voor '%s'." % (responsible.name(), event))

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
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.team.pk)

  event = Event.objects.get(pk=request.POST.get("event", ""))
  responsible = Profile.objects.get(pk=request.POST.get("responsible", ""))

  # Edit duty
  duty.timetable = table
  duty.event = event
  duty.responsible = responsible
  duty.comments = request.POST.get("comments", "").strip()

  duty.save()

  return redirect('timetable-detail-page', id=table.id)

@login_required
def timetable_teamleader_duty_edit(request, id):
  duty = TimetableDuty.objects.get(pk=id)

  # Check if user is teamleader of the new/old timetable's team
  if not request.profile.teamleader_of(duty.timetable.team):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=duty.timetable.team.pk)

  # Return only tables which the user is admin of
  # Get all teams which the user is leader of
  leading_teams = TeamMember.objects.filter(profile=request.profile, is_admin=True).prefetch_related('team')

  # Get all corresponding timetables
  tables = Timetable.objects.filter(team__in=leading_teams.values('team'))

  # Get all future events
  events = Event.objects.filter(startdatetime__gte=datetime.today().date())\
      .order_by("startdatetime", "enddatetime", "title")

  # Get all teammembers
  members = TeamMember.objects.filter(team=duty.timetable.team)

  return render(request, 'teamleader/teamleader_duty_edit.html', {
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

  # Check if user is teamleader of the new/old timetable's team
  if not request.profile.teamleader_of(table.team):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.team.pk)

  duty.delete()

  return redirect('timetable-detail-page', id=table.pk)

@login_required
def timetable_teamleader_duty_new(request, id):
  table = Timetable.objects.get(pk=id)

  # Check if user is teamleader of the new/old timetable's team
  if not request.profile.teamleader_of(table.team):
    # Redirect to first public page
    return redirect('timetable-detail-page', id=table.team.pk)

  # Get all future events
  events = Event.objects.filter(startdatetime__gte=datetime.today().date())\
      .order_by("startdatetime", "enddatetime", "title")

  # set default selection to event without duty (belonging to this timetable)
  if events.exclude(duties__timetable=table.pk).exists():
    selected_event = events.exclude(duties__timetable=table.pk).first().pk
  else:
    selected_event = 0

  # Get all teammembers
  members = table.team.teammembers

  # set default selection to member which is last scheduled
  duties = table.duties.filter(event__enddatetime__gte=datetime.today().date()).order_by("-event__enddatetime", "-event__startdatetime")
  if duties.exists():
    # get only users that are still teammembers
    responsibles = duties.filter(responsible__in=members.values_list('profile', flat=True)).values_list('responsible', flat=True)

    unique_responsibles = uniqify(responsibles)

    # Add also the members who aren't scheduled for any duty yet
    b = members.values_list('profile', flat=True)
    all_responsibles = uniqify(unique_responsibles + uniqify(b))

    selected_member = all_responsibles[-1]
  else:
    selected_member = 0

  return render(request, 'teamleader/teamleader_duty.html', {
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

@login_required
@permission_required('agenda.add_service', raise_exception=True)
def services(request):
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
    print(startdatetime)

  return render(request, 'services/main.html', {
    'startdatetime': startdatetime,
  })

@login_required
@require_POST
@permission_required('agenda.add_service', raise_exception=True)
def services_add(request):
  date = str(request.POST.get("date", ""))

  # Ochtenddienst
  startdate = "%s %s:00" % (date, str(request.POST.get("starttime1", "09:30")))
  enddate = "%s %s:00" % (date, str(request.POST.get("endtime1", "11:00")))

  try:
    startdate = datetime.strptime(startdate, '%d-%m-%Y %H:%M:%S')
    enddate = datetime.strptime(enddate, '%d-%m-%Y %H:%M:%S')
  except ValueError:
    messages.error(request, 'Het formaat van de ingevulde datum en/of tijdstip klopt niet.')
    return redirect('services-page')

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
      return redirect('services-page')

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

  return redirect('services-page')

@login_required
@require_POST
@permission_required('agenda.change_service', raise_exception=True)
def services_edit_save(request, id):
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
    return redirect('services-page')

  service.startdatetime = startdate
  service.enddatetime = enddate
  service.title = request.POST.get("title", "").strip()
  service.minister = request.POST.get("minister", "").strip()
  service.theme = request.POST.get("theme", "").strip()
  service.comments = request.POST.get("comments", "").strip()
  service.description = request.POST.get("description", "").strip()

  service.save()

  messages.success(request, "Dienst is opgeslagen.")

  return redirect('services-page')

@login_required
@permission_required('agenda.change_service', raise_exception=True)
def services_edit(request, id):

  return render(request, 'services/edit.html', {
    'service': Service.objects.get(pk=id),
  })

@login_required
@permission_required('agenda.delete_service', raise_exception=True)
def services_delete(request, id):
  Service.objects.get(pk=id).delete()

  # Delete all duties of this service
  TimetableDuty.objects.filter(event=id).delete()

  messages.success(request, "Dienst is verwijderd.")

  return redirect('services-page')



# Team pages

@login_required
def teampage_control_members(request, id):
  team = Team.objects.get(pk=id)

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=id)

  members = team.teammembers.order_by('profile__first_name')

  # Get all profiles but exclude profiles that are already member
  memberspk = members.values_list('pk', flat=True)
  profiles = Profile.objects.all().order_by('last_name', 'first_name')\
    .exclude(team_membership__pk__in=memberspk)

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

  # Check if user is teamleader of this team
  if not request.profile.teamleader_of(team) and not request.user.has_perm('agenda.change_team'):
    # Redirect to first public page
    return redirect('teampage', id=team.pk)

  if profile is "0":
    messages.error(request, "Er is geen (geldig) lid gekozen om toe te voegen.")
    return redirect('teampage-control-members', id=team)

  # Check if profile is valid
  if TeamMember.objects.filter(team_id=team, profile_id=profile).exists():
    messages.error(request, "Het gekozen lid bestaat niet of maakt al deel uit van dit team.")
    return redirect('teampage-control-members', id=team)

  TeamMember.objects.create(
    team=Team.objects.get(pk=team),
    profile=Profile.objects.get(pk=profile),
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
  member.is_admin=True if request.POST.get("is_admin", False) else False
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

  if len(team.timetables):
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

  team.name = request.POST.get("name", "").strip()
  team.description = request.POST.get("description", "").strip()
  team.email = email
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
  })

@login_required
def teampage(request, id):
  team = Team.objects.get(pk=id)

  members = team.teammembers.order_by('role__name', 'profile__first_name')

  tables = team.timetables.order_by('title')

  # Render that stuff!
  return render(request, 'teampage/teampage.html', {
    'team': team,
    'is_admin': request.profile.teamleader_of(team),
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
def services_files(request, id=None):

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
def services_files_add(request):

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

  return redirect('services-files')

@login_required
@permission_required('agenda.change_eventfile', raise_exception=True)
@require_POST
def services_files_edit_save(request, id):

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
    return redirect('services-files-edit', id=id)

  return redirect('services-files')

@login_required
@permission_required('agenda.delete_eventfile', raise_exception=True)
def services_files_delete(request, id):

  ef = EventFile.objects.get(pk=id).delete()

  messages.success(request, 'Bestand is verwijderd.')

  return redirect('services-files')


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
  url(r'^roosters/$', timetables, name='timetable-list-page'),

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

  url(r'^team/(?P<id>\d+)/edit/save/$', teampage_control_edit_save, name='teampage-control-edit-save'),
  url(r'^team/(?P<id>\d+)/edit/$', teampage_control_edit, name='teampage-control-edit'),
  url(r'^team/(?P<id>\d+)/$', teampage, name='teampage'),

  url(r'^teams/(?P<id>\d+)/delete/$', globalteampage_delete, name='team-delete'),
  url(r'^teams/add/save/$', globalteampage_add, name='team-add-save'),
  url(r'^teams/add/$', globalteampage, name='team-add'),

  url(r'^roosters/diensten/add/$', services_add, name='services-page-add'),
  url(r'^roosters/diensten/(?P<id>\d+)/edit/save/$', services_edit_save, name='services-page-edit-save'),
  url(r'^roosters/diensten/(?P<id>\d+)/edit/$', services_edit, name='services-page-edit'),
  url(r'^roosters/diensten/(?P<id>\d+)/delete/$', services_delete, name='services-page-delete'),
  url(r'^roosters/diensten/$', services, name='services-page'),

  url(r'^roosters/diensten/bestanden/(?P<id>\d+)/delete/$', services_files_delete, name='services-files-delete'),
  url(r'^roosters/diensten/bestanden/(?P<id>\d+)/edit/save/$', services_files_edit_save, name='services-files-edit-save'),
  url(r'^roosters/diensten/bestanden/(?P<id>\d+)/edit/$', services_files, name='services-files-edit'),
  url(r'^roosters/diensten/bestanden/add/$', services_files_add, name='services-files-add'),
  url(r'^roosters/diensten/bestanden/$', services_files, name='services-files'),
]
