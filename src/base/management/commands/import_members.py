from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from base.models import *

from collections import Counter

from datetime import datetime
import argparse
import csv
import re

def parse_families(members):
  families = {}

  # detect family members by address
  for member in members:
    # unpack values
    titel, roepnaam, voorletter, voorvgsels, achternaam, straat, postcode, woonplaats, telefoon, wijk, geslacht, gebdatum, email, ltelefoon = member

    # skip columnnames (might repeat)
    if titel.strip() == "TITEL": continue

    # parse wijk
    wijk = int(wijk.strip())

    # parse gebdatum
    try:
      gebdatum = datetime.strptime(gebdatum.strip(), "%d-%m-%Y")
    except ValueError as e:
      gebdatum = None

    # parse email
    email = email.strip()
    if len(email) == 0:
      email = None

    # parse zip
    # make sure it's only 6 chars long and uppercase
    postcode = re.sub(r" ", "", postcode).upper()

    # parse phone
    phone = telefoon
    if not len(ltelefoon.strip()) == 0:
      phone = ltelefoon

    # update the family
    key = (straat.strip(), postcode.strip(), woonplaats.strip(), wijk, achternaam[0:3])
    family = families.get(key, [])
    family.append({
      "firstname": roepnaam.strip(),
      "initials": voorletter.strip(),
      "lastname": achternaam.strip(),
      "prefix": voorvgsels,
      "birthday": gebdatum,
      "phone": phone.strip(),
      "email": email
    })
    families[key] = family

  # detect family name
  families_named = {}
  for key, members in families.items():
    # include a little piece of the last name to seperate different families in one house
    straat, postcode, woonplaats, wijk, lstname = key

    # vote: majority lastname
    lastname = max(
      sorted(Counter(
              [m['lastname'] if (len(m['prefix']) == 0) else ("%s, %s" % (m['lastname'], m['prefix'])) for m in members]
      ).items()),
      key=lambda x: x[1]
    )[0]

    # vote: majority phone
    phone = max(
      Counter([m['phone'] for m in members]).items(),
      key=lambda x: x[1]
    )[0]

    families_named[(lastname, straat, postcode, woonplaats, phone, wijk)] = members

  return families_named

def print_families(families):
  for fam, members in families.items():
    print("Fam " + str(fam))
    for m in members:
      print("   - " + m)
    print()

def insert_families(families):
  for fam, members in families.items():
    lastname, straat, postcode, woonplaats, phone, wijk = fam

    wijk = Wijk.objects.get(pk=wijk)

    address = Address.objects.create(
      street=straat,
      zip=postcode,
      city=woonplaats,
      country="Nederland",
      wijk=wijk,
      phone=phone
    )

    family = Family.objects.create(lastname=lastname, address=address)

    for m in members:
      profiel = Profile.objects.create(
        first_name=m['firstname'],
        initials=m['initials'],
        last_name=m['lastname'],
        prefix=m['prefix'],
        email=m['email'],
        phone=m['phone'],
        birthday=m['birthday'],
        family=family,
        role_in_family=None
      )

class Command(BaseCommand):
  help = 'Import a .csv members file'

  def add_arguments(self, parser):
    parser.add_argument('member-file', nargs=1, type=str)

  def handle(self, *args, **options):
    member_fp = options['member-file'][0]

    with open(member_fp, 'r', newline='', encoding="ISO-8859-1") as fh:
      members = csv.reader(fh, delimiter=';')
      families = parse_families(members)

    with transaction.atomic():
      insert_families(families)

      print("\n\n<===== DONE =====>\n")
      print("Warning: Please correct the familymembers of the family 'Ee, van'. The mother has been given her own family...")
      print("Warning: Please add Marit and Lianne Zantinge to the family Strijbos...")
      print()
