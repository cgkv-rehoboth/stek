from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django import http

from base.models import *

"""
  url(r'^leden/(?P<id>\d+)/$', addressbook.profile, name='profile'),
  url(r'^families/$', addressbook.family_list, name='addressbook-family-list'),
  url(r'^families/(?P<id>\d+)/$', addressbook.family, name='addressbook-family-detail'),
  url(r'^adresboek/favorites/$', addressbook.favorites, name='addressbook-favorites-list'),
  url(r'^adresboek/favorites/(?P<id>\d+)/$', addressbook.detail, name='addressbook-favorites-post'),
"""

@login_required
def profile_list(request):
  return render(request, 'addressbook/profiles.html')

@login_required
def favorite_list(request):
  return render(request, 'addressbook/favorites.html')

@login_required
def profile_detail(request, id):
  return render(request, 'profile.html', {
    'p': Profile.objects.get(pk=id)
  })

urls = [
  url(r'^login$', auth_views.login, {'template_name':'login.html'}, name='login'),
  url(r'^adresboek/$', profile_list, name='profile-list'),
  url(r'^adresboek/favorieten/$', favorite_list, name='favorite-list'),
  url(r'^profiel/(?P<id>\d+)/$', profile_detail, name='profile-detail'),
]
