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
from django import http
from django.core import serializers
from django.contrib import messages
from datetime import datetime, timedelta

from .forms import LoginForm

from agenda.models import *
from base.models import *

from .forms import UploadImageForm

@login_required
def profile_list(request):
  return render(request, 'addressbook/profiles.html')

@login_required
def favorite_list(request):
  return render(request, 'addressbook/favorites.html')

@login_required
def team_list(request, pk=None):
  teams = Team.objects.all()\
                      .prefetch_related("teammembers")

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
def profile_detail(request, pk):
  profiel = Profile.objects.get(pk=pk)
  memberships = TeamMember.objects\
                          .prefetch_related("team")\
                          .filter(profile__pk=pk)

  saddr = request.profile.best_address()
  daddr = profiel.best_address()

  googlemaps = "https://www.google.com/maps/dir/%s/%s/" % (saddr, daddr)

  return render(request, 'profile.html', {
    'p': profiel,
    'googlemaps': googlemaps,
    'memberships': memberships
  })

@login_required
def profile_detail_edit(request, pk):
  profile = Profile.objects.prefetch_related("address").get(pk=pk)

  if not request.profile.pk == profile.pk:
    return HttpResponse(status=404)


  return render(request, 'profile_edit.html', {
    'p': profile,
    'a': serializers.serialize('json', [ profile.best_address() ])
  })

@login_required
@require_POST
def profile_detail_edit_save(request, pk):
  profile = Profile.objects.get(pk=pk)

  if not request.profile.pk == profile.pk:
    return HttpResponse(status=404)

  # Address, only save when react form was loaded
  if request.POST.get("form-loaded", False):
    zip = request.POST.get("zip", "").replace(" ", "").upper()
    number = request.POST.get("number", "").replace(" ", "").upper()
    street = "%s %s" % (request.POST.get("street", ""), number)
    city = request.POST.get("city", "")
    country = request.POST.get("country", "")
    phone = request.POST.get("phone", "").replace(" ", "")

    # Validate
    if not (zip and street and city and country):
      # Wrong validation
      messages.error(request, "Er is geen juist adres ingevuld. Een juist adres bestaat uit een postcode, straatnaam, woonplaats en landnaam.")
      return redirect('profile-detail-page', pk=pk)

    # Save address
    adr, created = Address.objects.get_or_create(zip=zip, street=street, city=city, country=country)

    adr.phone = phone
    adr.save()


    # Check for 'verhuizing'
    if request.POST.get("verhuizing", False):  # check with current address (profile OR family)
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
    print(request.POST.get("birthday", ""))
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

  messages.success(request, "Gegevens zijn opgeslagen")

  return redirect('profile-detail-page', pk=pk)

@login_required
@require_POST
def profile_pic_edit_save(request, pk):
  profile = Profile.objects.get(pk=pk)

  if not request.profile.pk == int(pk):
    return HttpResponse(status=404)

  form = UploadImageForm(request.POST, request.FILES)
  if form.is_valid():
    profile.photo.delete()
    profile.photo=request.FILES['file']
    profile.save(request.POST.get("center", "0.5,0.5"))
    messages.success(request, "Profielfoto is opgeslagen")

  return redirect('profile-detail-page', pk=pk)

@login_required
def profile_pic_delete(request, pk):
  profile = Profile.objects.get(pk=pk)

  if not request.profile.pk == int(pk):
    return HttpResponse(status=404)

  profile.photo.delete()

  messages.success(request, "Profielfoto is verwijderd")

  return redirect('profile-detail-page', pk=pk)

def logout_view(request):
  logout(request)
  return redirect('login')

def change_password_done(request):
  messages.success(request, "Wachtwoord is gewijzigd")
  return redirect('profile-detail-page', pk=request.profile.pk)

@login_required
def dashboard(request):

  # Get ruilrequests
  def filterTeamleaderTables():
    # Get all the tables linked to the team(s) the user is in
    for table in Timetable.objects.filter(team__members__pk=request.profile.pk).exclude(team__isnull=True):
      if request.profile.teamleader_of(table.team):
        yield table

  mytables = list(filterTeamleaderTables())

  ruilrequests = RuilRequest.objects\
                   .filter(timetableduty__timetable__in=mytables, timetableduty__event__enddatetime__gte=datetime.today().date())\
                   .order_by("timetableduty__event__startdatetime", "timetableduty__event__enddatetime")[:4]

  # Get timetableduties
  maxweeks = datetime.today().date() + timedelta(weeks=4)
  duties = TimetableDuty.objects\
             .prefetch_related('ruilen')\
             .filter(responsible=request.profile, event__enddatetime__gte=datetime.today().date(), event__startdatetime__lte=maxweeks)\
             .order_by("event__startdatetime", "event__enddatetime")

  for duty in duties:
    for req in duty.ruilen.all():
      # sanity check
      # only a single request can pass this check
      # due to the uniqueness constraint on requests
      if req.profile == duty.responsible:
        duty.ruilrequest = req

  return render(request, 'dashboard.html', {
    'ruilrequests': ruilrequests,
    'duties': duties
  })

urls = [
  # auth
  url(r'^login$', auth_views.login, {'template_name':'login.html', 'authentication_form': LoginForm}, name='login'),
  url(r'^logout', logout_view, name='logout'),
  url(r'^wachtwoord_wijzigen/done/', change_password_done, name='password_change_done'),
  url(r'^wachtwoord_wijzigen', auth_views.password_change, name='password_change'),
  url(r'^wachtwoord_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
  url(r'^wachtwoord_reset/$', auth_views.password_reset, {
    'html_email_template_name': 'emails/password_reset.html',
  }, name='password_reset'),
  url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
  url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),

  # addressbook
  url(r'^adresboek/$', profile_list, name='profile-list-page'),
  url(r'^adresboek/favorieten/$', favorite_list, name='favorite-list-page'),
  url(r'^adresboek/families/$', family_list, name='family-list-page'),
  url(r'^adresboek/families/(?P<pk>\d+)/$', family_list, name='family-detail-page'),

  # teams
  url(r'^teams/$', team_list, name='team-list-page'),
  url(r'^teams/(?P<pk>\d+)/$', team_list, name='team-detail-page'),

  # profiles
  url(r'^profiel/(?P<pk>\d+)/foto/save/$', profile_pic_edit_save, name='profile-pic-edit-save'),
  url(r'^profiel/(?P<pk>\d+)/foto/delete/$', profile_pic_delete, name='profile-pic-delete'),
  url(r'^profiel/(?P<pk>\d+)/edit/save/$', profile_detail_edit_save, name='profile-detail-page-edit-save'),
  url(r'^profiel/(?P<pk>\d+)/edit/$', profile_detail_edit, name='profile-detail-page-edit'),
  url(r'^profiel/(?P<pk>\d+)/$', profile_detail, name='profile-detail-page'),

  # dashboard
  url(r'^dashboard$', dashboard, name='dashboard'),
]
