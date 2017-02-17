from django.core.management.base import BaseCommand
from agenda.models import *
from base.models import Profile
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from html.parser import HTMLParser
from django.utils.html import strip_tags


def send_reminder_mail(duty, resp, email):
  templateTXT = get_template('emails/remind_timetableduties.txt')
  templateHTML = get_template('emails/remind_timetableduties.html')

  event = str(duty.event)
  if duty.responsible_family:
    event += " door familie %s" % str(duty.responsible_family.lastname)

  data = Context({
    'resp'     : resp,
    'duty'     : duty,
    'event'    : event,
    'protocol' : 'https',
    'domain'   : get_current_site(None).domain,
    'sendtime' : datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
  })

  subject = "Herinnering aan %s [PREVIEW]" % duty.event

  messageTXT = templateTXT.render(data)
  messageHTML = templateHTML.render(data)

  if duty.timetable.team.remindermail:
    # Decode possible special chars and remove HTML tags
    h = HTMLParser()

    messageTXT = h.unescape(strip_tags(messageTXT))

  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [email, ]

  send_mail(subject, messageTXT, from_email, to_emails, html_message=messageHTML)


class Command(BaseCommand):
  help = 'Sending preview email reminder for the first duty of the specified team to a specific emailaddress.'

  def add_arguments(self, parser):
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('team', type=int)
    parser.add_argument('email')

  def handle(self, *args, **options):
    dryrun = options['dryrun']
    team = options['team']
    email = options['email']

    # ensure email is present
    if not email or len(email) == 0:
      print("[FAILURE] No emailaddress given.")
      return

    if not team or not isinstance(team, int) or team < 1:
      print("[FAILURE] No valid Team given.")
      return

    if dryrun:
      print(">> Dry-run: only reporting")
      print()
      dryrun = True

    ## Check if member wants a reminder
    # Get member
    resp = Profile.objects.filter(email=email).first()
    if not resp:
      print("[WARNING] No valid Profile given, random profile being chosen.")
      resp = Profile.objects.first()

    # Get valid duty
    duty = TimetableDuty.objects.filter(event__enddatetime__gte=datetime.today().date(), timetable__team__pk=team).first()
    if not duty:
      duty = TimetableDuty.objects.filter(timetable__team__pk=team).order_by('event__startdatetime').first()
      if not duty:
        print("[FAILURE] No valid Duty found.")
        return

    # Send mail
    print("[SUCCESS] Sending reminder to %s for duty %s." % (resp.name(), duty))
    if not dryrun:
      send_reminder_mail(duty, resp, email)
