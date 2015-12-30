from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django.contrib.auth.forms import AuthenticationForm
from django import http
from django_tables2 import RequestConfig
from .tables import *

from .models import *

def login(request):
  if request.method == 'POST':
    form = AuthenticationForm(data=request.POST)
    submitted = True
  else:
    form = AuthenticationForm()
    submitted = False

  if submitted and form.is_valid():
    return http.HttpResponseRedirect('/')
  else:
    return render(request, 'login.html', { 'form': AuthenticationForm() })

@login_required
def addressbookSearch(request):
  extra = None
  data = "Send some search query please."

  if 'search' in request.POST and not request.POST['search'] == "":
    # Get search fields
    extra = request.POST.getlist('fields[]')

    # Add search query at begin of this list for template usage
    extra.insert(0, request.POST['search'])

    # Get search data
    query = Q()
    for v in request.POST['search'].split(' '):
      subquery = Q()
      if 'first_name' in extra:
        subquery |= Q(user__first_name__contains=v)
      if 'last_name' in extra:
        subquery |= Q(user__last_name__contains=v)
      if 'address' in extra:
        subquery |= Q(address__street__contains=v)
      query &= subquery

    # Generate table
    data = ProfileTable(Profile.objects.filter(query).order_by('user__last_name', 'user__first_name'))
    RequestConfig(request, paginate={'per_page': 30}).configure(data)

  return render(request, 'addressbookSearch.html', {
    'data': data,
    'extra': extra
  })

@login_required
def addressbookPersons(request):
  table = ProfileTable(Profile.objects.all())
  RequestConfig(request, paginate={'per_page': 30}).configure(table)

  return render(request, 'addressbookPersons.html', {
    'page': 'persons',
    'table': table,
  })


@login_required
def addressbookFavorites(request):
  table = ProfileTable(Profile.objects.all())
  RequestConfig(request, paginate={'per_page': 30}).configure(table)

  return render(request, 'addressbookPersons.html', {
    'page': 'favorites',
    'table': table,
  })

@login_required
def addressbookFavoritesPost(request, action=None):
  if 'id' in request.GET:
    # Check if id is already a favorite, if yes: remove it!
    # Todo: Do some fancy adding stuff
    return JsonResponse({'hasErrors': False})
  return JsonResponse({'hasErrors': True})


@login_required
def addressbookFamily(request, id=0):
  # Get all families including the members (which are sorted by age)
  data = Family.objects.prefetch_related(Prefetch('members', queryset=Profile.objects.order_by('birthday'))).order_by('lastname')

  return render(request, 'addressbookFamily.html', {
    'page': 'families',
    'data': data,
    'id': int(id)
  })

@login_required
def addressbookProfile(request, id=None):
  return render(request, 'profile.html', {
    'p': Profile.objects.get(pk=id)
  })


'''
# Not gonna use this one anymore
@login_required
def addressbookx(request):
  table = 'persons'
  if 'table' in request.GET:
    table = request.GET['table']

  if table == 'persons':
    table = ProfileTable(Profile.objects.all())
    RequestConfig(request, paginate={ 'per_page': 30}).configure(table)
    return render(request, 'addressbook.html', {'table': table})
  elif table == 'families':
    users = User.objects.all()
    if 'order_by' in request.GET:
      users = users.order_by(request.GET['order_by'])
    # Render that stuff!
    return render(request, 'addressbook.html', {
      'users': users,
    })
'''

urls = [
  url(r'^login$', login, name='login'),
  url(r'^adresboek/$', addressbookPersons, name='addressbook-list'),
  url(r'^adresboek/leden/$', addressbookPersons, name='addressbook-persons-list'),
  url(r'^adresboek/families/$', addressbookFamily, name='addressbook-family-list'),
  url(r'^adresboek/families/(?P<id>\d+)/$', addressbookFamily, name='addressbook-family-detail'),
  url(r'^adresboek/favorites/$', addressbookFavorites, name='addressbook-favorites-list'),
  url(r'^adresboek/favorites/(?P<action>\w+)/$', addressbookFavoritesPost, name='addressbook-favorites-post'),
  url(r'^adresboek/profiel/(?P<id>\d+)/$', addressbookProfile, name='profile'),
]
