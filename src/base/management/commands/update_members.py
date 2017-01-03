from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from base.models import *

from collections import Counter

from datetime import datetime
import argparse
import csv
import re


def update_profile(old, new, dryrun):
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

  old.first_name  = new['ROEPNAAM'].strip()
  old.initials    = new['VOORLETTER'].strip()
  old.last_name   = new['ACHTERNAAM'].strip()
  old.prefix      = new['VOORVGSELS'].strip()
  old.phone       = new['LTELEFOON'].strip()
  old.email       = new['EMAIL'].strip()
  old.birthday    = new['GEBDATUM']

  if new['GVOLGORDE'].strip() == "1":
    old.role_in_family = 'DAD'
  elif new['GVOLGORDE'].strip() == "2":
    old.role_in_family = 'MUM'
  else:
    old.role_in_family = 'KID'

  old.voornamen   = new['VOORNAMEN'].strip()
  old.geslacht    = new['GESLACHT'].strip()
  old.soortlid    = new['SOORTLID'].strip()
  old.burgerstaat = new['BURGSTAAT'].strip()
  old.doopdatum   = new['DOOPDATUM']
  old.belijdenisdatum = new['BELDATUM']
  old.huwdatum    = new['HUWDATUM']
  old.lidnr       = new['LIDNR']
  old.gvolgorde   = int(new['GVOLGORDE'].strip())
  old.titel       = new['TITEL'].strip()
  
  # Check for address
  if old.address:
    # parse zip
    # make sure it's only 6 chars long and uppercase
    new['POSTCODE'] = re.sub(r" ", "", new['POSTCODE']).upper()

    old.address.street = new['STRAAT'].strip()
    old.address.zip    = new['POSTCODE']
    old.address.city   = new['WOONPLAATS'].strip()
    old.address.phone  = new['TELEFOON'].strip()
    old.address.wijk   = Wijk.objects.get(id=int(new['WIJK'].strip()))

    # Save it
    if not dryrun:
      old.address.save()
      print("[SUCCES] Saved address %s" % old.address)
    else:
      print("[FAILURE] Failed to save address %s" % old.address)

  if not dryrun:
    old.save()
    print("[SUCCES] Saved %s" % old)
  else:
    print("[FAILURE] Failed to save %s" % old)


def update_family(old, new, dryrun):
  old.lastname     = new['GEZINSNAAM'].strip()
  old.prefix       = new['GEZVOORVGS'].strip()
  old.aanhef = new['GEZAANHEF'].strip()
  old.gezinsnr     = new['GEZINSNR']

  # Don't update address, this may be a personal address
  # leave this to update_families.py

  if not dryrun:
    old.save()
    print("[SUCCES] Saved %s" % old)
  else:
    print("[FAILURE] Failed to save %s" % old)


class Command(BaseCommand):
  help = 'Import a .csv members file'

  def add_arguments(self, parser):
    parser.add_argument('member-file', nargs=1, type=str)
    parser.add_argument('--dryrun', action='store_true')

  def handle(self, *args, **options):
    member_fp = options['member-file'][0]
    dryrun = options['dryrun']

    errors = []
    checked_profiles = []
    checked_families = []

    headers = [
      'GEZINSNAAM', 'GEZAANHEF', 'GEZVOORVGS', 'STRAAT', 'POSTCODE', 'WOONPLAATS', 'TELEFOON', 'WIJK', 'GEZINSNR',
      'ACHTERNAAM', 'VOORVGSELS', 'VOORNAMEN', 'ROEPNAAM', 'VOORLETTER', 'GESLACHT', 'SOORTLID', 'BURGSTAAT',
      'GEBDATUM', 'DOOPDATUM', 'BELDATUM', 'HUWDATUM', 'LIDNR', 'GVOLGORDE', 'TITEL', 'EMAIL', 'LTELEFOON'
    ]

    with open(member_fp, 'r', newline='', encoding="ISO-8859-1") as fh:
      members = csv.DictReader(fh, delimiter=',')

      # Check for needed headers
      missingheaders = list(set(headers) - set(members.fieldnames))
      if missingheaders:
        if len(missingheaders) > 1:
          print("De kolommen %s ontbreken." % ', '.join(missingheaders))
        else:
          print("De kolom %s ontbreekt." % missingheaders[0])
        return

      oldfamilies = []
      for m in members:
        ##
        # Parse some items first
        #

        # parse gebdatum
        try:
          m['GEBDATUM'] = datetime.strptime(m['GEBDATUM'].strip(), "%d-%m-%Y").date()
        except ValueError as e:
          m['GEBDATUM'] = None

        # parse integers
        m['LIDNR'] = int(m['LIDNR'])
        m['GEZINSNR'] = int(m['GEZINSNR'])

        famname = m['GEZINSNAAM'] if len(m['GEZVOORVGS']) == 0 else ("%s, %s" % (m['GEZINSNAAM'], m['GEZVOORVGS'])).strip()

        ##
        # Start the real work
        #

        # Get profile
        p = Profile.objects.filter(birthday=m['GEBDATUM'], family__lastname=famname)

        if len(p) == 0:
          # Try another way to find the profile
          p = Profile.objects.filter(birthday=m['GEBDATUM'], last_name=m['ACHTERNAAM'], prefix=m['VOORVGSELS'])

          if len(p) == 0:
            # Try again
            p = Profile.objects.filter(birthday=m['GEBDATUM'], first_name=m['ROEPNAAM'], initials=m['VOORLETTER'])

            if len(p) == 0:
              # Final try
              p = Profile.objects.filter(first_name=m['ROEPNAAM'], initials=m['VOORLETTER'], last_name=m['ACHTERNAAM'],
                                         prefix=m['VOORVGSELS'])

              if len(p) == 0:
                # Give up: Not found
                errors.append('Geen online profiel gevonden voor lidnummer %d (%s %s %s).' % (m['LIDNR'], m['ROEPNAAM'],
                                                                                              m['VOORVGSELS'],
                                                                                              m['ACHTERNAAM']))

        if p:
          if len(p) > 1:
            # Twin things: be more accurate
            p = p.filter(first_name=m['ROEPNAAM'])
            if len(p) > 1:
              p = p.filter(initials=m['VOORLETTER'])

          p = p.first()

          # Update profile info
          update_profile(p, m, dryrun)

          # Record this one as done
          checked_profiles.append(p.pk)

          ## Family
          # Check if family already has been compared
          if not m['GEZINSNR'] in oldfamilies:
            if not p.family:
              print('[WARNING] %s doesn\'t belongs to a family' % p)
              errors.append('%s heeft geen familie' % p)

            else:
              # Update family info
              update_family(p.family, m, dryrun)

              # Record this one as done
              checked_families.append(p.family.pk)
              oldfamilies.append(m['GEZINSNR'])

    ##
    # Get the newly added profiles/families
    #

    # Get remaining profiles
    for p in Profile.objects.exclude(pk__in=checked_profiles).order_by('last_name', 'first_name'):
      print('[INFO] Nothing in CSV found for %s' % p)

    # Get remaining families
    for f in Family.objects.exclude(pk__in=checked_families).order_by('lastname'):
      print('[INFO] Nothing in CSV found for %s' % f)

    for e in errors:
      print('[INFO] %s' % e)
