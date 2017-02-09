
from django.conf.urls import include, url
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from agenda.models import *
from base.models import *

import base.views
import base.api
import agenda.views
import agenda.api
import public.views
import public.api

from machina.app import board

def account_to_profile(request, pk):
  try:
    pf = User.objects.get(pk=pk).profile.pk
    return redirect('profile-detail-page', pk=pf)
  except ObjectDoesNotExist:
    return redirect('profile-list-page')


def account_to_profile_edit(request):
  return redirect('profile-detail-page-edit', pk=request.profile.pk)

urlpatterns = [
  url(r'^member/profile/', include([
#    url(r'^(?P<pk>\d+)/posts/$', 'base.views.profile_detail'),
    url(r'^(?P<pk>\d+)/$', account_to_profile),
    url(r'^edit/$', account_to_profile_edit),
  ])),
  url(r'^gebruiker/profiel/', include([
#    url(r'^(?P<pk>\d+)/posts/$', 'base.views.profile_detail'),
    url(r'^(?P<pk>\d+)/$', account_to_profile),
    url(r'^edit/$', account_to_profile_edit),
  ])),

  url(r'', include(board.urls)),
]
