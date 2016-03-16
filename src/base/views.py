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
    .prefetch_related(Prefetch('members', queryset=Profile.objects.order_by('birthday')))\
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
                          .filter(user__pk=pk)

  return render(request, 'profile.html', {
    'p': profiel,
    'memberships': memberships
  })

urls = [
  url(r'^login$', auth_views.login, {'template_name':'login.html'}, name='login'),
  url(r'^adresboek/$', profile_list, name='profile-list-page'),
  url(r'^adresboek/favorieten/$', favorite_list, name='favorite-list-page'),
  url(r'^adresboek/families/$', family_list, name='family-list-page'),
  url(r'^adresboek/families/(?P<pk>\d+)/$', family_list, name='family-detail-page'),
  url(r'^teams/$', team_list, name='team-list-page'),
  url(r'^profiel/(?P<pk>\d+)/$', profile_detail, name='profile-detail-page'),
]
