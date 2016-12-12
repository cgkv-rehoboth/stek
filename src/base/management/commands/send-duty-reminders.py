from django.core.management.base import BaseCommand
from agenda.models import TimetableDuty
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.conf import settings


def send_reminder_mail(duty, resp):
  template = get_template('emails/remind_timetableduties.txt')

  if duty.comments:
    comments = "Hierbij is ook het volgende commentaar gegeven:\n\n%s\n" % duty.comments
  else:
    comments = ""

  event = str(duty.event)
  if duty.responsible_family:
    event += " door familie %s" % str(duty.responsible_family.lastname)

  data = Context({
    'name': resp.name(),
    'date': duty.event.startdatetime.strftime("%d-%m-%Y"),
    'timetable': duty.timetable,
    'event': event,
    'comments': comments,
    'sendtime': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
  })

  subject = "Herinnering aan %s" % duty.event

  message = template.render(data)

  from_email = settings.DEFAULT_FROM_EMAIL

  to_emails = [resp.email, ]

  send_mail(subject, message, from_email, to_emails)


class Command(BaseCommand):
  help = 'Sending email reminders for all upcoming duties in the next week.'

  def add_arguments(self, parser):
    parser.add_argument('--dryrun', action='store_true')

  def handle(self, *args, **options):
    dryrun = options['dryrun']

    if dryrun:
      print(">> Dry-run: only reporting")
      print()
      dryrun = True

    maxweeks = datetime.today().date() + timedelta(weeks=1)
    # Select only profiles and not families
    duties = TimetableDuty.objects.filter(event__enddatetime__gte=datetime.today().date(), event__startdatetime__lte=maxweeks)

    for d in duties:
      if d.responsible_family:
        resp = d.responsible_family.members_sorted()[0]

        if not resp:
          print("[FAILURE] Could not get a profile for family %s." % d.responsible_family.lastname)
          continue

      else:
        resp = d.responsible

      # ensure email is present
      if resp.email is None or len(resp.email) == 0:
        print("[FAILURE] Profile '%s' has no emailaddress." % (resp.name()))
        continue

      # Send mail
      print("[SUCCESS] Sending reminder to %s for duty %s." % (resp.name(), d))
      if not dryrun:
        send_reminder_mail(d, resp)
