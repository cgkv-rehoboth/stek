from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.http import *
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django import http
from django.core import serializers
from django.contrib import messages
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
import json

from .forms import LoginForm, UploadImageForm

from agenda.models import *
from base.models import *

from machina.apps.forum_member.models import *


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
def profile_list(request):
  return render(request, 'addressbook/profiles.html')

@login_required
def favorite_list(request):
  return render(request, 'addressbook/favorites.html')

@login_required
def team_list(request, pk=None):
  teams = Team.objects.all().prefetch_related("teammembers").order_by('name')

  for i, u in enumerate(teams):
    teams[i].teammembersSorted = teams[i].teammembers.all().order_by('role__name', 'family__lastname', 'profile__first_name')

  if pk is not None:
    pk = int(pk)

  return render(request, 'addressbook/teams.html', {
    'teams': teams,
    'id': pk
  })

@login_required
def family_list(request, pk=None):
  data = Family.objects\
    .prefetch_related(
      Prefetch('members', queryset=Profile.objects.order_by('birthday')),
      'address'
    )\
    .order_by('lastname')

  # get dictionary of favorites
  favorites = dict(
    [ (v.favorite.pk, True) for v in Favorites.objects.filter(owner=request.profile) ])

  if pk is not None:
    pk = int(pk)

  return render(request, 'addressbook/families.html', {
    'data': data,
    'favorites': favorites,
    'id': pk
  })

@login_required
def profile_detail(request, pk=None):
  # Set default pk (when redirected from e.g. Machina)
  if (pk==None):
    pk = request.profile.pk

  profiel = Profile.objects.get(pk=pk)
  memberships = TeamMember.objects\
                          .prefetch_related("team")\
                          .filter(Q(profile=profiel)|Q(family=profiel.family))\
                          .order_by('team__name')

  # Remove double memberships (like profile AND family), filter on (i.)team
  memberships = uniqify(memberships, lambda i: i.team)

  is_my_favorite = profiel.is_favorite_for(request.profile)

  saddr = request.profile.best_address()
  daddr = profiel.best_address()

  googlemaps = "https://www.google.com/maps/dir/%s/%s/" % (saddr, daddr)

  return render(request, 'profile.html', {
    'p': profiel,
    'is_my_favorite': is_my_favorite,
    'googlemaps': googlemaps,
    'memberships': memberships
  })

@login_required
def profile_detail_edit(request, pk):
  profile = Profile.objects.prefetch_related("address").get(pk=pk)

  if not request.profile.pk == profile.pk and not request.profile.family == profile.family:
    return HttpResponse(status=404)


  return render(request, 'profile_edit.html', {
    'p': profile,
    'a': serializers.serialize('json', [ profile.best_address() ])
  })

@login_required
@require_POST
def profile_detail_edit_save(request, pk):
  profile = Profile.objects.get(pk=pk)

  if not request.profile.pk == profile.pk and not request.profile.family == profile.family:
    return HttpResponse(status=404)

  # Address, only save when react form was loaded
  if request.POST.get("form-loaded", False):
    zip = request.POST.get("zip", "").replace(" ", "").upper()
    number = request.POST.get("number", "").replace(" ", "").upper()
    street = request.POST.get("street", "").strip()
    city = request.POST.get("city", "")
    country = request.POST.get("country", "")
    phone = request.POST.get("phone", "").replace(" ", "")

    # Validate
    if not (zip and number and street and city and country):
      # Wrong validation
      messages.error(request, "Er is geen juist adres ingevuld. Een juist adres bestaat uit een postcode, straatnaam, woonplaats en landnaam.")
      return redirect('profile-detail-page', pk=pk)

    street = "%s %s" % (street, number)

    # Check for 'verhuizing'
    if request.POST.get("verhuizing", False) == "true":  # check with current address (profile OR family)
      if request.POST.get("verhuizing-options", "") is "0":
        # Wrong option choosen
        messages.error(request, "Adreswijziging mislukt. Kies een geldige verhuisoptie.")
        return redirect('profile-detail-page', pk=pk)

      # Save address
      #adr, created = Address.objects.filter(family=None, profile=None).get_or_create(zip=zip, street=street, city=city, country=country)

      adr = Address.objects.filter(family=None, profile=None, zip=zip, street=street, city=city, country=country).first()
      if not adr:
        # Create address if it doesn't exists
        adr = Address.objects.create(zip=zip, street=street, city=city, country=country)

      adr.phone = phone
      adr.save()

      if request.POST.get("verhuizing-options", "") is "1":
        # Check if this is the family address
        if profile.family.address is adr:
          profile.address = None
        else:
          profile.address = adr

      elif request.POST.get("verhuizing-options", "") is "2":
        if not hasattr(adr, "family"):
          profile.address = None
          profile.family.address = adr

          profile.family.save()

        #else:
          # Address is already coupled to a other family
          # todo: mulptiple families may live at the same address (like grandparents, parents and their kids)

  # parse gebdatum
  try:
    bday = datetime.strptime(request.POST.get("birthday", "").strip(), "%d-%m-%Y")
  except ValueError as e:
    # Wrong validation

    # Tell them something went good ...
    if request.POST.get("form-loaded", False):
      messages.success(request, "Adresgegevens opgeslagen.")

    # ... and something went wrong
    messages.error(request, "De geboortedatum klopt niet volgens de syntax 'dd-mm-jjjj', zoals 31 december 1999 gescreven wordt als '31-12-1999'.")
    return redirect('profile-detail-page', pk=pk)

  # Save rest of the profile stuff
  profile.first_name = request.POST.get("first_name", "").replace('"', '').strip()
  profile.initials = request.POST.get("initials", "").strip()
  profile.prefix = request.POST.get("prefix", "").strip()
  profile.last_name = request.POST.get("last_name", "").replace('"', '').strip()
  profile.birthday = bday
  profile.email = request.POST.get("email", "").lower().strip()
  profile.phone = request.POST.get("phone-privat", "").strip()

  # todo: add profile validation

  profile.save()

  messages.success(request, "Gegevens zijn opgeslagen.")

  return redirect('profile-detail-page', pk=pk)

@login_required
@require_POST
def profile_pic_edit_save(request, pk):
  profile = Profile.objects.get(pk=pk)

  if not request.profile.pk == int(pk) and not request.profile.family == profile.family:
    return HttpResponse(status=404)

  form = UploadImageForm(request.POST, request.FILES)
  if form.is_valid():
    profile.photo.delete()
    profile.photo=request.FILES['file']
    profile.save(request.POST.get("center", "0.5,0.5"))
    messages.success(request, "Profielfoto is opgeslagen.")

    # Save profile pic (avatar) for the forum profile
    if profile.user:
      try:
        fp = ForumProfile.objects.get(user_id=profile.user.pk)
        if(fp):
          fp.avatar = profile.photo
          fp.save()
      except ObjectDoesNotExist:
        pass


  return redirect('profile-detail-page', pk=pk)

@login_required
def profile_pic_delete(request, pk):
  profile = Profile.objects.get(pk=pk)

  if not request.profile.pk == int(pk) and not request.profile.family == profile.family:
    return HttpResponse(status=404)

  profile.photo.delete()

  # Save profile pic (avatar) for the forum profile
  if profile.user:
    try:
      fp = ForumProfile.objects.get(pk=profile.user.pk)
      if(fp):
        fp.avatar = profile.photo
        fp.save()
    except ObjectDoesNotExist:
      pass

  messages.success(request, "Profielfoto is verwijderd.")

  return redirect('profile-detail-page', pk=pk)

def logout_view(request):
  logout(request)
  return redirect('login')

def change_password_done(request):
  messages.success(request, "Wachtwoord is gewijzigd.")
  return redirect('profile-detail-page', pk=request.profile.pk)

def email_reset_done(request):

  return render(request, 'registrations/password_reset_done.html')

def reset_password_done(request):
  messages.success(request, "Het nieuwe wachtwoord is opgeslagen. U kunt nu hieronder inloggen.")
  return redirect('login')

@login_required
def dashboard(request):

  ## Get services for this week
  maxweeks = datetime.today().date() + timedelta(weeks=1)
  services = Service.objects.filter(enddatetime__gte=datetime.today().date(), startdatetime__lte=maxweeks).order_by("startdatetime", "enddatetime")

  serviceslist = []
  for service in services:
    s = vars(service)
    s['url'] = service.url()

    duties = []
    for duty in service.duties.all():
      d = {
        'comments': duty.comments,
        'timetable': {
          'id': duty.timetable.id,
          'url': reverse('timetable-detail-page', kwargs={'id': duty.timetable.id}),
          'title': duty.timetable.title,
          'color': duty.timetable.color,
          'team': duty.timetable.team.name,
        },
#        'responsible': {
#          'id': duty.responsible.id,
#          'url': reverse('profile-detail-page', kwargs={'pk': duty.responsible.id}),
#          'name': duty.responsible.name(),
#        },
      }

      duties.append(d)

    # Add duties to this service
    s['duties'] = duties

    # Get EvenFiles with all information
    files = []
    for file in service.files.all():
      f = vars(file)

      f.update({
        'filesize': file.filesize(),
        'type': file.type(),
        'url': file.type(),
        'file': file.file.url
      })

      f.pop('_state')
      f.pop('_event_cache')
      files.append(f)

    # Add files to this service
    s['files'] = files

    s.pop('_state')
    serviceslist.append(s)

  # JSON encoder for the datetime fields
  class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
      if isinstance(obj, datetime):
        return str(obj)
      return json.JSONEncoder.default(self, obj)

  # Convert it all to JSON
  servicesJSON = json.dumps(serviceslist, cls=DatetimeEncoder)


  ## Get ruilrequests
  def filterTeamleaderTables():
    # Get all the tables linked to the team(s) the user is in
    for table in Timetable.objects.filter(team__members__pk=request.profile.pk).exclude(team__isnull=True):
      if request.profile.teamleader_of(table.team):
        yield table

  mytables = list(filterTeamleaderTables())

  ruilrequests = RuilRequest.objects\
                   .filter(timetableduty__timetable__in=mytables, timetableduty__event__enddatetime__gte=datetime.today().date())\
                   .order_by("timetableduty__event__startdatetime", "timetableduty__event__enddatetime")[:4]


  ## Get timetableduties
  maxweeks = datetime.today().date() + timedelta(weeks=4)
  duties = TimetableDuty.objects\
             .filter(Q(responsible=request.profile) | Q(responsible_family=request.profile.family), event__enddatetime__gte=datetime.today().date(), event__startdatetime__lte=maxweeks)\
             .order_by("event__startdatetime", "event__enddatetime")

  for duty in duties:
    for req in duty.ruilen.all():
      # sanity check
      # only a single request can pass this check
      # due to the uniqueness constraint on requests
      if req.profile == duty.responsible or req.profile.family == duty.responsible_family:
        duty.ruilrequest = req

  is_birthday = request.profile.birthday.strftime('%d-%m') == datetime.today().date().strftime('%d-%m')

  return render(request, 'dashboard.html', {
    'is_birthday': is_birthday,
    'services': servicesJSON,
    'ruilrequests': ruilrequests,
    'duties': duties
  })

urls = [
  # auth
  url(r'^login$', RedirectView.as_view(url='login/', permanent=True)),
  url(r'^login/$', auth_views.login, {'template_name':'login.html', 'authentication_form': LoginForm}, name='login'),

  url(r'^logout$', RedirectView.as_view(url='logout/', permanent=True)),
  url(r'^logout/$', logout_view, name='logout'),

  url(r'^wachtwoord/wijzigen/done/$', change_password_done, name='password_change_done'),
  url(r'^wachtwoord/wijzigen/$', auth_views.password_change, {
    'template_name': 'registrations/password_change_form.html',
  }, name='password_change'),

  url(r'^wachtwoord/vergeten/done/$', email_reset_done, name='password_reset_done'),
  url(r'^wachtwoord/vergeten/$', auth_views.password_reset, {
    'template_name': 'registrations/password_reset_form.html',
    'html_email_template_name': 'emails/password_reset.html',
  }, name='password_reset'),

  url(r'^reset/done/$', reset_password_done, name='password-reset-done'),
  #url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
  url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {
    'template_name': 'registrations/password_reset_confirm.html',
    'post_reset_redirect': 'password-reset-done'
  }, name='password_reset_confirm'),

  # addressbook
  url(r'^adresboek$', RedirectView.as_view(url='adresboek/', permanent=True)),
  url(r'^adresboek/$', profile_list, name='profile-list-page'),
  url(r'^adresboek/favorieten/$', favorite_list, name='favorite-list-page'),
  url(r'^adresboek/families/$', family_list, name='family-list-page'),
  url(r'^adresboek/families/(?P<pk>\d+)/$', family_list, name='family-detail-page'),

  # teams
  url(r'^teams$', RedirectView.as_view(url='teams/', permanent=True)),
  url(r'^teams/$', team_list, name='team-list-page'),
  url(r'^teams/(?P<pk>\d+)/$', team_list, name='team-detail-page'),

  # profiles
  url(r'^profiel/(?P<pk>\d+)/foto/save/$', profile_pic_edit_save, name='profile-pic-edit-save'),
  url(r'^profiel/(?P<pk>\d+)/foto/delete/$', profile_pic_delete, name='profile-pic-delete'),
  url(r'^profiel/(?P<pk>\d+)/edit/save/$', profile_detail_edit_save, name='profile-detail-page-edit-save'),
  url(r'^profiel/(?P<pk>\d+)/edit/$', profile_detail_edit, name='profile-detail-page-edit'),
  url(r'^profiel/(?P<pk>\d+)/$', profile_detail, name='profile-detail-page'),

  # dashboard
  url(r'^dashboard$', RedirectView.as_view(url='dashboard/', permanent=True)),
  url(r'^dashboard/$', dashboard, name='dashboard'),
]
