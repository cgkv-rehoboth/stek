from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
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
def addressbook(request, page='persons'):
  data=None
  extra=None

  # Check which table/view needs to be loaded
  if page == 'persons':
    data = ProfileTable(Profile.objects.all())
    RequestConfig(request, paginate={'per_page': 30}).configure(data)

  elif page == 'families':
    # Get all families including the members (which are sorted by age)
    data = Family.objects.prefetch_related(Prefetch('members', queryset=FamilyMember.objects.order_by('user__profile__birthday'))).order_by('lastname')

  elif page == 'search' and 'search' in request.POST and not request.POST['search'] == "":
    # Get search fields
    extra = request.POST.getlist('fields[]')

    # Add search query at begin of this list for template usage
    extra.insert(0, request.POST['search'])

    # Get search data
    query = Q()
    if 'first_name' in extra:
      query |= Q(user__first_name__contains=request.POST['search'])
    if 'last_name' in extra:
      query |= Q(user__last_name__contains=request.POST['search'])
    if 'address' in extra:
      query |= Q(address__street__contains=request.POST['search'])

    # Generate table
    data = ProfileTable(Profile.objects.filter(query))
    RequestConfig(request, paginate={'per_page': 30}).configure(data)

  return render(request, 'addressbook.html', {
    'page': page,
    'data': data,
    'extra': extra
  })

def addressbooksearch(query):
  return "You looked for: " + query;

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
  #url(r'^adresboek/search/(?P<query>\w+)/$', addressbooksearch, name='addressbook-search'),
  url(r'^adresboek/(?P<page>\w+)/$', addressbook, name='addressbook-detail'),
  url(r'^adresboek/$', addressbook, name='addressbook-list'),
  url(r'^profiel/(?P<id>\d+)/$', addressbook, name='profile'),
]
