from django.core.management.base import BaseCommand, CommandError
from base.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
import unidecode
from django.utils.crypto import get_random_string
from datetime import date
from dateutil.relativedelta import relativedelta
import time

class NewAccountPasswordResetForm(PasswordResetForm):
  def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
    # Set subject of password-reset mail
    subject_template_name = "emails/new_account_subject.txt"

    return super().send_mail(
      subject_template_name,
      email_template_name,
      context,
      from_email,
      to_email,
      html_email_template_name="emails/new_account_send_password.html"
    )

def collect_accountless(profiles):
    for prof in profiles:
        # check if user has an account
        if prof.user is None:
            yield prof

def send_reset_email(profile, username):
    # create a new user and associate it with the profile, also add a random password, otherwhise the PasswordResetForm won't work
    user = User.objects.create_user(
      username=username,
      email=profile.email,
      first_name=profile.first_name,
      last_name=profile.last_namef(),
      password=get_random_string(50)
    )
    profile.user = user
    profile.save()

    # init the password reset form
    reset_form = NewAccountPasswordResetForm({ "email": profile.email })
    if reset_form.is_valid():
      reset_form.save()
      return True
    else:
      print("[FAILURE]: Ongeldig password-reset-form voor e-mailadres '%s'" % profile.email)
      return False


class Command(BaseCommand):
  help = 'Create accounts for profiles without.'

  def add_arguments(self, parser):
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('profiles', nargs="*", default=[])

  def handle(self, *args, **options):
    dryrun = options['dryrun']
    profiles = options['profiles']
    if dryrun:
      print(">> Proefdraaien: alleen berichten, geen uitvoering")
      print()
      dryrun = True

    if len(profiles) > 0:
      profiles = Profile.objects.filter(pk__in=profiles)
      print(">> Alleen accounts maken voor:")
      for p in profiles:
        print(">> .. %s (%s)" % (p.last_namep(), p.first_name))
      print()
    else:
      limitdate = date.today() - relativedelta(years=14)
      print(">> Profielen ophalen met een geboortedatum eerder dan %s " % limitdate)
      profiles = Profile.objects.filter(birthday__lte=limitdate).order_by('last_name', 'first_name')

    for prof in collect_accountless(profiles):
      profname = "%s (%s)" % (prof.last_namep(), prof.first_name)

      # ensure an email account is set
      if prof.email is None or len(prof.email) == 0:
        print("[FAILURE] Profiel {0:32} heeft geen account, maar ook geen e-mailadres".format("'%s'" % profname))
        continue

      ## think of a clever username
      # Remove all non alphabatic and special chars
      firstname = ''.join(e for e in unidecode.unidecode(prof.first_name.lower()) if e.isalnum())
      lastname = prof.last_namef().split('-').pop()
      lastname = ''.join(e for e in unidecode.unidecode(lastname.lower()) if e.isalnum())

      # Merge it for an username
      username = "%s.%s" % (firstname, lastname)

      # ensure the username is not taken
      if User.objects.filter(username=username).exists():
        print("[FAILURE] Profiel '%s' heeft geen account, maar de gebruikersnaam '%s' bestaat al" % (
          profname,
          username
        ))
        continue

      if not dryrun:
        x = send_reset_email(prof, username)
        time.sleep(1)

      if dryrun or x:
        print("[SUCCESS] Mail verstuurd naar %s | %s" % (prof.email.rjust(32), profname))
      else:
        print("[FAILURE] Mislukt om een mail te versturen naar %s | %s" % (prof.email.rjust(32), profname))
