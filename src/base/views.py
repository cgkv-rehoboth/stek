from django.contrib.auth.decorators import login_required, permission_required
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
from django.core import management
from io import StringIO
from datetime import date
from dateutil.relativedelta import relativedelta
import csv
import tempfile
import json
import re
import sys

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


def get_delimiter(file):
  firstline = file.readline()
  file.seek(0)
  if firstline.find(';') != -1:
    return ';'
  elif firstline.find('|') != -1:
    return '|'
  else:
    return ','


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
    messages.error(request, "De geboortedatum klopt niet volgens de syntax 'dd-mm-jjjj', zoals 31 december 1999 geschreven wordt als '31-12-1999'.")
    return redirect('profile-detail-page', pk=pk)

  # Save rest of the profile stuff
  profile.first_name = request.POST.get("first_name", "").replace('"', '').strip()
  profile.initials = request.POST.get("initials", "").strip().replace(" ", "").upper()
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


@login_required
@permission_required('base.add_profile', raise_exception=True)
def addressbook_management(request):
  headers = [
    'GEZINSNAAM', 'GEZAANHEF', 'GEZVOORVGS', 'STRAAT', 'POSTCODE', 'WOONPLAATS', 'TELEFOON', 'WIJK', 'GEZINSNR',
    'ACHTERNAAM', 'VOORVGSELS', 'VOORNAMEN', 'ROEPNAAM', 'VOORLETTER', 'GESLACHT', 'SOORTLID', 'BURGSTAAT',
    'GEBDATUM', 'DOOPDATUM', 'BELDATUM', 'HUWDATUM', 'LIDNR', 'GVOLGORDE', 'TITEL', 'EMAIL', 'LTELEFOON'
  ]
  address_headers = ['STRAAT', 'POSTCODE', 'WOONPLAATS', 'TELEFOON', 'WIJK']
  family_headers = ['GEZINSNAAM', 'GEZAANHEF', 'GEZVOORVGS', 'GEZINSNR'] + address_headers

  limitdate = date.today() - relativedelta(years=14)
  new_accounts = Profile.objects.filter(user=None, birthday__lte=limitdate).exclude(email='').exclude(email=None)
  
  return render(request, 'addressbook/beheer/main.html', {
    'headers': headers,
    'family_headers': family_headers,
    'new_accounts': len(new_accounts),
  })


@login_required
@permission_required('base.add_profile', raise_exception=True)
@require_POST
def addressbook_differences(request):
  errors = []
  profile_differences = {}
  family_differences = {}
  checked_profiles = []
  checked_families = []
  new_profiles = []
  new_families = []
  members_file = request.FILES.get('members_file')
  families_file = request.FILES.get('families_file')
  
  # Check for file(s)
  if not (members_file or families_file):
    messages.error(request, "Er dient tenminste één bestand geüpload te worden.")
    return redirect('addressbook-management')

  headers = [
    'GEZINSNAAM', 'GEZAANHEF', 'GEZVOORVGS', 'STRAAT', 'POSTCODE', 'WOONPLAATS', 'TELEFOON', 'WIJK', 'GEZINSNR',
    'ACHTERNAAM', 'VOORVGSELS', 'VOORNAMEN', 'ROEPNAAM', 'VOORLETTER', 'GESLACHT', 'SOORTLID', 'BURGSTAAT',
    'GEBDATUM', 'DOOPDATUM', 'BELDATUM', 'HUWDATUM', 'LIDNR', 'GVOLGORDE', 'TITEL', 'EMAIL', 'LTELEFOON'
  ]
  address_headers = ['STRAAT', 'POSTCODE', 'WOONPLAATS', 'TELEFOON', 'WIJK']
  family_headers = ['GEZINSNAAM', 'GEZAANHEF', 'GEZVOORVGS', 'GEZINSNR'] + address_headers

  ##
  # Declare some functions
  #

  def get_profile_differences(old, new):
    # Difference, saved as [key => (old value, new value)]
    diff = {}
      
    # parse date
    try:
      old['DOOPDATUM'] = datetime.strptime(old['DOOPDATUM'].strip(), "%d-%m-%Y").date()
    except ValueError as e:
      old['DOOPDATUM'] = None
  
    # parse date
    try:
      old['BELDATUM'] = datetime.strptime(old['BELDATUM'].strip(), "%d-%m-%Y").date()
    except ValueError as e:
      old['BELDATUM'] = None
  
    # parse date
    try:
      old['HUWDATUM'] = datetime.strptime(old['HUWDATUM'].strip(), "%d-%m-%Y").date()
    except ValueError as e:
      old['HUWDATUM'] = None
      
    # parse GVOLGORDE
    old['GVOLGORDE'] = int(old['GVOLGORDE'].strip())

    newl = {
      'GEZINSNR': new.family.gezinsnr,
      'STRAAT': '',
      'POSTCODE': '',
      'WOONPLAATS': '',
      'TELEFOON': '',
      'WIJK': '',
      'ACHTERNAAM': new.last_name,
      'VOORVGSELS': new.prefix,
      'VOORNAMEN': new.voornamen,
      'ROEPNAAM': new.first_name,
      'VOORLETTER': new.initials,
      'GESLACHT': new.geslacht,
      'SOORTLID': new.soortlid,
      'BURGSTAAT': new.burgerstaat,
      'GEBDATUM': new.birthday,
      'DOOPDATUM': new.doopdatum,
      'BELDATUM': new.belijdenisdatum,
      'HUWDATUM': new.huwdatum,
      'LIDNR': new.lidnr,
      'GVOLGORDE': new.gvolgorde,
      'TITEL': new.titel,
      'EMAIL': new.email if new.email else '',
      'LTELEFOON': new.phone
    }
    
    # If personal address is set
    if new.address:
      newl.update({
        'STRAAT': new.address.street,
        'POSTCODE': new.address.zip,
        'WOONPLAATS': new.address.city,
        'TELEFOON': new.address.phone,
        'WIJK': new.address.wijk.id if new.address.wijk else '',
      })

    for h in list(set(headers) - set(family_headers)) + ['GEZINSNR']:
      if not old[h] == newl[h]:
        diff[h] = [old[h], newl[h]]
        
    # Familyrole
    if not ((old['GVOLGORDE'] == 1 and new.role_in_family == 'DAD') or
              (old['GVOLGORDE'] == 2 and new.role_in_family == 'MUM') or
              (old['GVOLGORDE'] > 2 and new.role_in_family == 'KID')):
      if old['GVOLGORDE'] == 1:
        oldvolgorde = "%s (%s)" % (old['GVOLGORDE'], [y[1] for x, y in enumerate(Profile.ROLE_CHOICES) if y[0] == 'DAD'][0])
      elif old['GVOLGORDE'] == 2:
        oldvolgorde = "%s (%s)" % (old['GVOLGORDE'], [y[1] for x, y in enumerate(Profile.ROLE_CHOICES) if y[0] == 'MUM'][0])
      else:
        oldvolgorde = "%s (%s)" % (old['GVOLGORDE'], [y[1] for x, y in enumerate(Profile.ROLE_CHOICES) if y[0] == 'KID'][0])
        
      if 'GVOLGORDE' in diff:
        diff['GVOLGORDE'] = [oldvolgorde, "%s / %s" % (newl['GVOLGORDE'], new.get_role_in_family_display())]
      else:
        diff['GVOLGORDE'] = [oldvolgorde, new.get_role_in_family_display()]

    # if personal adres, check it
    if new.address:
      for h in address_headers:
        if not old[h] == newl[h]:
          diff[h] = [old[h], newl[h]]

    if diff:
      diff['profile'] = new

    return diff

  def get_family_differences(old, new):
    # Difference, saved as [key => (old value, new value)]
    diff = {}

    newl = {
      'GEZINSNAAM': new.lastname,
      'GEZAANHEF': new.aanhef,
      'GEZVOORVGS': new.prefix,
      'STRAAT': new.address.street,
      'POSTCODE': new.address.zip,
      'WOONPLAATS': new.address.city,
      'TELEFOON': new.address.phone,
      'WIJK': new.address.wijk.id,
      'GEZINSNR': new.gezinsnr,
    }

    for h in family_headers:
      if not old[h] == newl[h]:
        diff[h] = [old[h], newl[h]]

    if diff:
      diff['family'] = new

    return diff

  ##
  # Main function for profiles
  #

  if members_file:
    # Create a temp file
    with tempfile.NamedTemporaryFile() as tf:
      # Copy the uploaded file to the temp file
      for chunk in members_file.chunks():
        tf.write(chunk)
  
      # Save contents to file on disk
      tf.flush()
  
      # Read file
      with open(tf.name, 'r', encoding="ISO-8859-1") as fh:
        members = csv.DictReader(fh, delimiter=get_delimiter(fh))
  
        # Check for needed headers
        missingheaders = list(set(headers) - set(members.fieldnames))
        if missingheaders:
          if len(missingheaders) > 1:
            messages.error(request, "De kolommen <strong>%s</strong> ontbreken in het ledenbestand." % ', '.join(missingheaders))
          else:
            messages.error(request, "De kolom <strong>%s</strong> ontbreekt in het ledenbestand." % missingheaders[0])
          return redirect('addressbook-management')
  
        oldfamilies = []
        for l in members:
  
          ##
          # Parse some items first
          #
  
          # parse gebdatum
          try:
            l['GEBDATUM'] = datetime.strptime(l['GEBDATUM'].strip(), "%d-%m-%Y").date()
          except ValueError as e:
            l['GEBDATUM'] = None
  
          #  parse phone
          # if len(l['LTELEFOON'].strip()) == 0:
          #   l['LTELEFOON'] = l['TELEFOON']
  
          # parse zip
          # make sure it's only 6 chars long and uppercase
          l['POSTCODE'] = re.sub(r" ", "", l['POSTCODE']).upper()
  
          # parse integers
          l['LIDNR'] = int(l['LIDNR'])
          l['WIJK'] = int(l['WIJK'])
          l['GEZINSNR'] = int(l['GEZINSNR'])
  
          ##
          # Start the real work
          #
  
          # Get profile
          p = Profile.objects.filter(lidnr=l['LIDNR'])
  
          if len(p) == 0:
            # Try again
            p = Profile.objects.filter(birthday=l['GEBDATUM'], last_name=l['ACHTERNAAM'], prefix=l['VOORVGSELS'])
  
            if len(p) == 0:
              # Try another way to find the profile
              famname = l['GEZINSNAAM'] if len(l['GEZVOORVGS']) == 0 else ("%s, %s" % (l['GEZINSNAAM'], l['GEZVOORVGS'])).strip()
              
              p = Profile.objects.filter(birthday=l['GEBDATUM'], family__lastname=famname)
  
              if len(p) == 0:
                # And again
                p = Profile.objects.filter(birthday=l['GEBDATUM'], first_name=l['ROEPNAAM'], initials=l['VOORLETTER'])
  
                if len(p) == 0:
                  # And again...
                  p = Profile.objects.filter(first_name=l['ROEPNAAM'], initials=l['VOORLETTER'],
                                             last_name=l['ACHTERNAAM'], prefix=l['VOORVGSELS'])
  
                  if len(p) == 0:
                    # Give up: Not found
                    errors.append('Geen online profiel gevonden voor lidnummer %d (%s %s %s).' % (
                      l['LIDNR'], l['ROEPNAAM'], l['VOORVGSELS'], l['ACHTERNAAM']
                    ))
  
          if p:
            if len(p) > 1:
              # Twin things: be more accurate
              p = p.filter(first_name=l['ROEPNAAM'])
              if len(p) > 1:
                p = p.filter(initials=l['VOORLETTER'])
  
            p = p.first()
  
            # Get profile differences
            difference = get_profile_differences(l, p)
            if difference:
              profile_differences[l['LIDNR']] = difference
  
            # Record this one as done
            checked_profiles.append(p.pk)
            
            ## Family
            # Check if family needs to be compared (due to missing file) and if family already has been compared
            if not families_file and not l['GEZINSNR'] in oldfamilies and p.family:
              # Get family differences
              difference = get_family_differences(l, p.family)
              if difference:
                family_differences[l['GEZINSNR']] = difference
  
              # Record this one as done
              checked_families.append(p.family.pk)
              oldfamilies.append(l['GEZINSNR'])
            
  ##
  # Main function for families
  #

  if families_file:
    # Create a temp file
    with tempfile.NamedTemporaryFile() as tf:
      # Copy the uploaded file to the temp file
      for chunk in families_file.chunks():
        tf.write(chunk)
  
      # Save contents to file on disk
      tf.flush()
  
      # Read file
      with open(tf.name, 'r', encoding="ISO-8859-1") as fh:
        families = csv.DictReader(fh, delimiter=get_delimiter(fh))
  
        # Check for needed headers
        missingheaders = list(set(family_headers) - set(families.fieldnames))
        if missingheaders:
          if len(missingheaders) > 1:
            messages.error(request, "De kolommen <strong>%s</strong> ontbreken in het gezinsbestand." % ', '.join(missingheaders))
          else:
            messages.error(request, "De kolom <strong>%s</strong> ontbreekt in het gezinsbestand." % missingheaders[0])
          return redirect('addressbook-management')

        for m in families:
          ##
          # Parse some items first
          #
  
          # parse zip
          # make sure it's only 6 chars long and uppercase
          m['POSTCODE'] = re.sub(r" ", "", m['POSTCODE']).upper()
  
          # parse integers
          m['WIJK'] = int(m['WIJK'])
          m['GEZINSNR'] = int(m['GEZINSNR'])
  
          ##
          # Start the real work
          #
  
          # Get family
          p = Family.objects.filter(gezinsnr=m['GEZINSNR'])

          if len(p) == 0:
            # Try again
            p = Family.objects.filter(lastname=m['GEZINSNAAM'], prefix=m['GEZVOORVGS'])
      
            if len(p) == 0:
              # Give up: Not found
              famname = m['GEZINSNAAM'] if len(m['GEZVOORVGS']) == 0 else (
              "%s, %s" % (m['GEZINSNAAM'], m['GEZVOORVGS'])).strip()

              if len(p) == 0:
                # Try again
                p = Family.objects.filter(lastname=famname, prefix='')
              
                errors.append('Geen online familie gevonden voor familienummer %d (%s).' % (m['GEZINSNR'], famname))
  
          if p:
            if len(p) > 1:
              # Twin things: be more accurate
              p = p.filter(address__zip=m['POSTCODE'])
      
              if len(p) > 1:
                # Get over it
                p = p.filter(address__street=m['STRAAT'])
        
                if len(p) > 1:
                  # PLEASE
                  p = p.filter(address__phone=m['TELEFOON'])
    
            p = p.first()
    
            # Get family differences
            difference = get_family_differences(m, p)
            if difference:
              family_differences[m['GEZINSNR']] = difference

            # Record this one as done
            checked_families.append(p.pk)

  ##
  # Get the newly added profiles/families
  #
  if members_file:
    # Get remaining profiles
    for p in Profile.objects.exclude(pk__in=checked_profiles).order_by('last_name', 'first_name'):
      new = {
        'profile': p,
        'GEZINSNAAM': p.family.lastname,
        'GEZVOORVGS': p.family.prefix,
        'GEZAANHEF': p.family.aanhef,
        'GEZINSNR': p.family.gezinsnr,
        'STRAAT': '',
        'POSTCODE': '',
        'WOONPLAATS': '',
        'TELEFOON': '',
        'WIJK': '',
        'ACHTERNAAM': p.last_name,
        'VOORVGSELS': p.prefix,
        'ROEPNAAM': p.first_name,
        'VOORLETTER': p.initials,
        'GEBDATUM': p.birthday,
        'GVOLGORDE': p.get_role_in_family_display(),
        'EMAIL': p.email if p.email else '',
        'LTELEFOON': p.phone
      }
  
      # If personal address is set
      if p.address:
        new.update({
          'STRAAT': p.address.street,
          'POSTCODE': p.address.zip,
          'WOONPLAATS': p.address.city,
          'TELEFOON': p.address.phone,
          'WIJK': p.address.wijk.id,
        })
  
      # Add profile to the list
      new_profiles.append(new)

  # Get remaining families, always, even if families_file is not set,
  # because families are also checked in the profilecheck
  for f in Family.objects.exclude(pk__in=checked_families).order_by('lastname'):
    famname = f.lastname.split(', ')
    new = {
      'family': f,
      'GEZINSNAAM': famname[0],
      'GEZVOORVGS': famname[1] if len(famname) > 1 else '',
      'STRAAT': f.address.street,
      'POSTCODE': f.address.zip,
      'WOONPLAATS': f.address.city,
      'TELEFOON': f.address.phone,
      'WIJK': f.address.wijk.id,
    }

    # Add family to the list
    new_families.append(new)

  return render(request, 'addressbook/beheer/difference.html', {
    'errors': errors,
    'headers': headers,
    'family_headers': family_headers,
    'new_families': new_families,
    'new_profiles': new_profiles,
    'family_differences': family_differences,
    'profile_differences': profile_differences,
  })


@login_required
@permission_required('base.add_profile', raise_exception=True)
@require_POST
def addressbook_add(request):
  errors = []
  created_profiles = []
  created_families = []
  members_file = request.FILES.get('members_file')
  
  # Check for file(s)
  if not members_file:
    messages.error(request, "Er dient een bestand geüpload te worden.")
    return redirect('addressbook-management')
    
  headers = [
    'GEZINSNAAM', 'GEZAANHEF', 'GEZVOORVGS', 'STRAAT', 'POSTCODE', 'WOONPLAATS', 'TELEFOON', 'WIJK', 'GEZINSNR',
    'ACHTERNAAM', 'VOORVGSELS', 'VOORNAMEN', 'ROEPNAAM', 'VOORLETTER', 'GESLACHT', 'SOORTLID', 'BURGSTAAT',
    'GEBDATUM', 'DOOPDATUM', 'BELDATUM', 'HUWDATUM', 'LIDNR', 'GVOLGORDE', 'TITEL', 'EMAIL', 'LTELEFOON'
  ]

  def create_family(new):
    ## Create address
    # parse zip
    # make sure it's only 6 chars long and uppercase
    new['POSTCODE'] = re.sub(r" ", "", new['POSTCODE']).upper()
    
    # Create address
    address = Address(
      street = new['STRAAT'].strip(),
      zip = new['POSTCODE'],
      city = new['WOONPLAATS'].strip(),
      phone = new['TELEFOON'].strip(),
      wijk = Wijk.objects.get(id=int(new['WIJK'].strip()))
    )
    address.save()
    
    ## Create family
    family = Family(
      lastname  = new['GEZINSNAAM'].strip(),
      prefix    = new['GEZVOORVGS'].strip(),
      aanhef    = new['GEZAANHEF'].strip(),
      gezinsnr  = new['GEZINSNR'],
      address   = address
    )
    family.save()
  
    return family
  
  def create_profile(new):
    # Get family
    family = Family.objects.get(gezinsnr=new['GEZINSNR'])

    # parse date
    try:
      new['DOOPDATUM'] = datetime.strptime(new['DOOPDATUM'].strip(), "%d-%m-%Y").date()
    except ValueError as e:
      new['DOOPDATUM'] = None
  
    # parse date
    try:
      new['BELDATUM'] = datetime.strptime(new['BELDATUM'].strip(), "%d-%m-%Y").date()
    except ValueError as e:
      new['BELDATUM'] = None
  
    # parse date
    try:
      new['HUWDATUM'] = datetime.strptime(new['HUWDATUM'].strip(), "%d-%m-%Y").date()
    except ValueError as e:
      new['HUWDATUM'] = None

    # Parse gvolgorde / family_role
    new['GVOLGORDE'] = int(new['GVOLGORDE'].strip())
    if new['GVOLGORDE'] == 1:
      role_in_family = 'DAD'
    elif new['GVOLGORDE'] == 2:
      role_in_family = 'MUM'
    else:
      role_in_family = 'KID'
      
    profile = Profile(
      phone       = new['LTELEFOON'].strip(),
      first_name  = new['ROEPNAAM'].strip(),
      initials    = new['VOORLETTER'].strip().replace(" ", "").upper(),
      last_name   = new['ACHTERNAAM'].strip(),
      prefix      = new['VOORVGSELS'].strip(),
      email       = new['EMAIL'].strip().lower(),
      birthday    = new['GEBDATUM'],
      family      = family,
      role_in_family = role_in_family,
      voornamen   = new['VOORNAMEN'].strip(),
      geslacht    = new['GESLACHT'].strip(),
      soortlid    = new['SOORTLID'].strip(),
      burgerstaat = new['BURGSTAAT'].strip(),
      doopdatum   = new['DOOPDATUM'],
      belijdenisdatum = new['BELDATUM'],
      huwdatum    = new['HUWDATUM'],
      lidnr       = new['LIDNR'],
      gvolgorde   = new['GVOLGORDE'],
      titel       = new['TITEL'].strip()
    )
    profile.save()
    
    return profile

  # Create a temp file
  with tempfile.NamedTemporaryFile() as tf:
    # Copy the uploaded file to the temp file
    for chunk in members_file.chunks():
      tf.write(chunk)
  
    # Save contents to file on disk
    tf.flush()
  
    # Read file
    with open(tf.name, 'r', encoding="ISO-8859-1") as fh:
      members = csv.DictReader(fh, delimiter=get_delimiter(fh))
    
      # Check for needed headers
      missingheaders = list(set(headers) - set(members.fieldnames))
      if missingheaders:
        if len(missingheaders) > 1:
          messages.error(request,
                         "De kolommen <strong>%s</strong> ontbreken in het ledenbestand." % ', '.join(missingheaders))
        else:
          messages.error(request, "De kolom <strong>%s</strong> ontbreekt in het ledenbestand." % missingheaders[0])
        return redirect('addressbook-management')
    
      oldfamilies = []
      for l in members:
      
        ##
        # Parse some items first
        #
      
        # parse gebdatum
        try:
          l['GEBDATUM'] = datetime.strptime(l['GEBDATUM'].strip(), "%d-%m-%Y").date()
        except ValueError as e:
          l['GEBDATUM'] = None
      
        # parse integers
        l['LIDNR'] = int(l['LIDNR'])
        l['GEZINSNR'] = int(l['GEZINSNR'])

        ##
        # Add family first
        # Check if family already exists and if family already has been compared
        if not l['GEZINSNR'] in oldfamilies:
          oldfamilies.append(l['GEZINSNR'])
          
          ## Check if family doesn't already exists
          # Get family
          f = Family.objects.filter(gezinsnr=l['GEZINSNR'])
          
          if len(f) == 0:
            # Try another search
            famname = l['GEZINSNAAM'] if len(l['GEZVOORVGS']) == 0 else (
              "%s, %s" % (l['GEZINSNAAM'], l['GEZVOORVGS'])).strip()
            
            f = Family.objects.filter(lastname=famname, prefix='')
            
          if len(f) > 0:
            # Profile already exists
            f = f.first()
            errors.append(
              'Online familie bestaat al voor familienummer %d (<a href="%s" title="Bekijk familie" target="_blank">%s</a>).' % (
                l['GEZINSNR'], reverse('family-detail-page', kwargs={'pk': f.pk}), f.lastnamep()
              ))
          else:
            # Create new family
            family = create_family(l)
    
            # Record this one as done
            created_families.append(family)
      
        ##
        # Start the real work
        #
      
        ## Make sure not to duplicate the profiles
        # Get profile
        p = Profile.objects.filter(lidnr=l['LIDNR'])

        if len(p) == 0:
          # Try again
          p = Profile.objects.filter(birthday=l['GEBDATUM'], last_name=l['ACHTERNAAM'], prefix=l['VOORVGSELS'],
                                     first_name=l['ROEPNAAM'], initials=l['VOORLETTER'])
              
        if len(p) > 0:
          # Profile already exists
          p = p.first()
          errors.append('Online profiel bestaat al voor lidnummer %d (<a href="%s" title="Bekijk profiel" target="_blank">%s</a>).' % (
            l['LIDNR'], reverse('profile-detail-page', kwargs={'pk': p.pk}), p.name()
          ))
        else:
          # Create new profile
          profile = create_profile(l)
        
          # Record this one as done
          created_profiles.append(profile)

  return render(request, 'addressbook/beheer/add.html', {
    'errors': errors,
    'created_families': created_families,
    'created_profiles': created_profiles,
  })


@login_required
@permission_required('auth.add_user', raise_exception=True)
@require_POST
def addressbook_users_spawn(request):
  failure = []
  info = []
  success = []

  # Create buffer to catch command output
  buf = StringIO()

  # Redirect stdout to buffer
  # DO NOT PRINT TO STDOUT AFTER THIS (before stdout is restored again)
  sysout = sys.stdout
  sys.stdout = buf

  # Execute command
  if request.POST.get('dryrun', False):
    management.call_command('spawn_accounts', '--dryrun', stdout=buf)
  else:
    management.call_command('spawn_accounts', stdout=buf)

  # Restore stdout
  sys.stdout = sysout

  # Store buffer value
  output = buf.getvalue()

  # Close buffer and clear memory
  buf.close()

  # Process
  for l in output.splitlines():
    sub = l[:9]
    # Select type
    if sub.find('[FAILURE]') != -1:
      failure.append(l[9:])
    elif sub.find('[SUCCESS]') != -1:
      success.append(l[9:])
    else:
      info.append(l)

  return render(request, 'addressbook/beheer/users_spawn.html', {
    'failure': failure,
    'info': info,
    'success': success,
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

  # Add profiles/families
  url(r'^adresboek/beheer/accounts/aanmaken/$', addressbook_users_spawn, name='addressbook-users-spawn'),
  url(r'^adresboek/beheer/mutaties/$', addressbook_differences, name='addressbook-differences'),
  url(r'^adresboek/beheer/toevoegen/$', addressbook_add, name='addressbook-add'),
  url(r'^adresboek/beheer/$', addressbook_management, name='addressbook-management'),
  #url(r'^adresboek/beheren/(?P<id>\d+)/edit/save/$', adresboek_admin_edit_save, name='adresboek-admin-edit-save'),
  #url(r'^adresboek/beheren/(?P<id>\d+)/edit/$', adresboek_admin_edit, name='adresboek-admin-edit'),
  #url(r'^adresboek/beheren/(?P<id>\d+)/delete/$', adresboek_admin_delete, name='adresboek-admin-delete'),
]
