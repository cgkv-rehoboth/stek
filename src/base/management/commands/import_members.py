from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from base.models import *

from collections import Counter

from datetime import datetime
import argparse
import csv

def parse_lastname(name):
  parts = name.split(' ')
  return ' '.join(parts[1:])

def parse_firstname(name):
  parts = name.split(' ')
  return parts[0]

def parse_families(members):
  families = {}

  # detect family members by address
  for member in members:
    # unpack values
    bday, name, street, zipno, city, phone, wijkno, email = member

    # skip columnnames (might repeat)
    if name.strip() == "NAAM": continue

    # parse wijkno
    wijkno = int(wijkno.strip())

    # parse bday
    try:
      bday = datetime.strptime(bday.strip(), "%m/%d/%Y")
    except ValueError as e:
      bday = None

    # parse email
    email = email.strip()
    if len(email) == 0:
      email = None

    # update the family
    key = (street.strip(), zipno.strip(), city.strip(), wijkno)
    family = families.get(key, [])
    family.append({
      "lastname": parse_lastname(name.strip()),
      "firstname": parse_firstname(name.strip()),
      "birthday": bday,
      "phone": phone.strip(),
      "email": email
    })
    families[key] = family

  # detect family name
  families_named = {}
  for key, members in families.items():
    street, zipno, city, wijkno = key

    # vote: majority lastname
    lastname = max(
      Counter([m['lastname'] for m in members]).items(),
      key=lambda x: x[1])[0]

    # vote: majority phone
    phone = max(
      Counter([m['phone'] for m in members]).items(),
      key=lambda x: x[1])[0]

    families_named[(lastname, street, zipno, city, phone, wijkno)] = members

  return families_named

def print_families(families):
  for fam, members in families.items():
    print("Fam " + str(fam))
    for m in members:
      print(m)
    print()

def insert_families(families):
  for fam, members in families.items():
    lastname, street, zipno, city, phone, wijkno = fam

    wijk = Wijk.objects.get(pk=wijkno)

    address = Address.objects.create(
      street=street,
      zip=zipno,
      city=city,
      country="Nederland",
      wijk=wijk,
      phone=phone
    )

    family = Family.objects.create(lastname=lastname, address=address)

    for m in members:
      profiel = Profile.objects.create(
        first_name=m['firstname'],
        last_name=m['lastname'],
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

    with open(member_fp, 'r', encoding='utf-8') as fh:
      members = csv.reader(fh, delimiter=',')
      families = parse_families(members)

    with transaction.atomic():
      insert_families(families)
