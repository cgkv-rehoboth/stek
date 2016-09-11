from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django import http

from agenda.models import *
from base.models import *

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

  return render(request, 'profile.html', {
    'p': profiel,
    'memberships': memberships
  })

urls = [
  # auth
  url(r'^login$', auth_views.login, {'template_name':'login.html'}, name='login'),
  url(r'^wachtwoord_reset/$', auth_views.password_reset, {
    'html_email_template_name': 'emails/password_reset.html'
  }, name='password_reset'),
  url(r'^wachtwoord_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
  url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
  url(r'^reset/done/$', auth_views.password_reset_done, name='password_reset_complete'),

  # addressbook
  url(r'^adresboek/$', profile_list, name='profile-list-page'),
  url(r'^adresboek/favorieten/$', favorite_list, name='favorite-list-page'),
  url(r'^adresboek/families/$', family_list, name='family-list-page'),
  url(r'^adresboek/families/(?P<pk>\d+)/$', family_list, name='family-detail-page'),

  # profiles
  url(r'^profiel/(?P<pk>\d+)/$', profile_detail, name='profile-detail-page'),

  # teams
  url(r'^teams/$', team_list, name='team-list-page'),
  url(r'^teams/(?P<pk>\d+)/$', team_list, name='team-detail-page'),
]
