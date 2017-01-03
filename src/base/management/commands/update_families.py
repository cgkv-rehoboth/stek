from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from base.models import *

from collections import Counter

from datetime import datetime
import argparse
import csv
import re


def update_family(old, new, dryrun):
  old.lastname     = new['GEZINSNAAM'].strip()
  old.prefix       = new['GEZVOORVGS'].strip()
  old.aanhef = new['GEZAANHEF'].strip()
  old.gezinsnr     = new['GEZINSNR']

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


class Command(BaseCommand):
  help = 'Import a .csv families file'

  def add_arguments(self, parser):
    parser.add_argument('family-file', nargs=1, type=str)
    parser.add_argument('--dryrun', action='store_true')

  def handle(self, *args, **options):
    family_fp = options['family-file'][0]
    dryrun = options['dryrun']

    errors = []
    checked_families = []

    headers = [
      'GEZINSNAAM', 'GEZAANHEF', 'GEZVOORVGS', 'STRAAT', 'POSTCODE', 'WOONPLAATS', 'TELEFOON', 'WIJK', 'GEZINSNR'
    ]

    with open(family_fp, 'r', newline='', encoding="ISO-8859-1") as fh:
      families = csv.DictReader(fh, delimiter=',')

      # Check for needed headers
      missingheaders = list(set(headers) - set(families.fieldnames))
      if missingheaders:
        if len(missingheaders) > 1:
          print("De kolommen %s ontbreken." % ', '.join(missingheaders))
        else:
          print("De kolom %s ontbreekt." % missingheaders[0])
        return

      for m in families:
        ##
        # Parse some items first
        #

        # parse integers
        m['GEZINSNR'] = int(m['GEZINSNR'])

        ##
        # Start the real work
        #

        # Get family
        p = Family.objects.filter(gezinsnr=m['GEZINSNR'])

        if len(p) == 0:
          famname = m['GEZINSNAAM'] if len(m['GEZVOORVGS']) == 0 else ("%s, %s" % (m['GEZINSNAAM'], m['GEZVOORVGS'])).strip()
            p = Family.objects.filter(lastname=famname, prefix='')

            if len(p) == 0:
              # Give up: Not found
              errors.append('Geen online familie gevonden voor familienummer %d (%s).' % (m['GEZINSNR'], famname))

        if p:
          if len(p) > 1:
            # Twin things: be more accurate
            p = p.filter(address__zip=re.sub(r" ", "", m['POSTCODE']).upper())

            if len(p) > 1:
              # Get over it
              p = p.filter(address__street=m['STRAAT'])

              if len(p) > 1:
                # PLEASE
                p = p.filter(address__phone=m['TELEFOON'])

          p = p.first()

          # Update family info
          update_family(p, m, dryrun)

          # Record this one as done
          checked_families.append(p.pk)

    ##
    # Get the newly added families
    #

    # Get remaining families
    for f in Family.objects.exclude(pk__in=checked_families).order_by('lastname'):
      print('[INFO] Nothing in CSV found for %s' % f)

    for e in errors:
      print('[INFO] %s' % e)
