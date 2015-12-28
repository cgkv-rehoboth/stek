from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf.urls import patterns, include, url
from django.contrib.auth.forms import AuthenticationForm
from django import http

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
def addressbook(request):
  users = User.objects.all()

  if 'order_by' in request.GET:
    users = users.order_by(request.GET['order_by'])

  # Render that stuff!
  return render(request, 'addressbook.html', {
    'users': users,
  })

urls = [
  url(r'^login$', login, name='login'),
  url(r'^adresboek', addressbook, name='addressbook')
]
