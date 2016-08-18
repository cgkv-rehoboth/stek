from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.http import *
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

@login_required
def profile_detail_edit(request, pk):
  profile = Profile.objects.get(pk=pk)

  print(request.profile.pk)
  print(profile.pk)
  if not request.profile.pk == profile.pk:
    return HttpResponse(status=404)

  return render(request, 'profile_edit.html', {
    'p': profile,
  })

@login_required
@require_POST
def profile_detail_edit_save(request, pk):
  profile = Profile.objects.get(pk=pk)

  if not request.profile.pk == profile.pk:
    return HttpResponse(status=404)

  profile.first_name = request.POST.get("first_name", "")
  profile.last_name = request.POST.get("last_name", "")
  profile.birthday = request.POST.get("birthday", "")
  profile.email = request.POST.get("email", "")
  profile.phone = request.POST.get("phone", "")

  profile.save()

  return redirect('profile-detail-page', pk=pk)


urls = [
  url(r'^login$', auth_views.login, {'template_name':'login.html'}, name='login'),
  url(r'^adresboek/$', profile_list, name='profile-list-page'),
  url(r'^adresboek/favorieten/$', favorite_list, name='favorite-list-page'),
  url(r'^adresboek/families/$', family_list, name='family-list-page'),
  url(r'^adresboek/families/(?P<pk>\d+)/$', family_list, name='family-detail-page'),
  url(r'^teams/$', team_list, name='team-list-page'),
  url(r'^teams/(?P<pk>\d+)/$', team_list, name='team-detail-page'),

  url(r'^profiel/(?P<pk>\d+)/edit/save/$', profile_detail_edit_save, name='profile-detail-page-edit-save'),
  url(r'^profiel/(?P<pk>\d+)/edit/$', profile_detail_edit, name='profile-detail-page-edit'),
  url(r'^profiel/(?P<pk>\d+)/$', profile_detail, name='profile-detail-page'),
]
