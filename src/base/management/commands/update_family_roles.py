from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from base.models import *
from django.core.exceptions import ObjectDoesNotExist

from collections import Counter

from datetime import datetime
import argparse
import csv
import re

def update_roles(members):
  profiles = []
  bad = []

  # detect family members by address
  for member in members:
    # unpack values
    gezinsnaam, gezaanhef, gezvoorvgs, straat, postcode, woonplaats, telefoon, wijk, gezinsnr, achternaam, voorvgsels, voornamen, roepnaam, voorletter, geslacht, gebdatum, gvolgorde, titel, email, ltelefoon = member

    # skip columnnames (might repeat)
    if gezinsnaam.strip() == "GEZINSNAAM": continue

    # parse gebdatum
    try:
      gebdatum = datetime.strptime(gebdatum.strip(), "%m/%d/%Y")
    except ValueError as e:
      gebdatum = None

    # get profile
    try:
      p = Profile.objects.get(initials=voorletter.strip(), last_name=achternaam.strip(), birthday=gebdatum)

      if gvolgorde.strip() == "1":
        p.role_in_family = 'DAD'
      elif gvolgorde.strip() == "2":
        p.role_in_family = 'MUM'
      else:
        p.role_in_family = 'KID'

      p.save()

      profiles.append(p)

      print("%s set to %s" % (p.name(), p.role_in_family))

    except ObjectDoesNotExist:
      bad.append("%s, %s, %s" % (roepnaam, achternaam, gebdatum))
      continue

  print("\nMissed ones:")
  for b in bad:
    print("   %s" %b)
  return profiles

def check_profiles(new):
  all = Profile.objects.all()

  diff = [x for x in all if x not in new]

  print("Missing profiles:")
  for d in diff:
    print("   %d: %s" % (d.pk, d))

class Command(BaseCommand):
  help = 'Update family roles.'

  def add_arguments(self, parser):
    parser.add_argument('file', nargs=1, type=str)

  def handle(self, *args, **options):
    file = options['file'][0]

    with open(file, 'r', newline='', encoding="ISO-8859-1") as fh:
      members = csv.reader(fh, delimiter=';')
      profiles = update_roles(members)

      print("Done.\n")

      check_profiles(profiles)

      print("Finished.\n")
