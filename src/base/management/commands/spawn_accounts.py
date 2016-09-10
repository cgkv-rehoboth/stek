from django.core.management.base import BaseCommand, CommandError
from base.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm

def collect_accountless(profiles):
    for prof in profiles:
        # check if user has an account
        if prof.user is None:
            yield prof

def send_reset_email(profile):
    # create a new user and associate it with the profile
    user = User.objects.create_user(username=profile.email, email=profile.email)
    profile.user = user

    # init the password reset form
    reset_form = PasswordResetForm({ "email": profile.email })
    if reset_form.is_valid():
        reset_form.save()


class Command(BaseCommand):
  help = 'Create accounts for profiles without.'

  def add_arguments(self, parser):
    parser.add_argument('--dryrun', action='store_true')

  def handle(self, *args, **options):
    dryrun = options['dryrun']
    if dryrun:
      print("Dry-run: only reporting")
      dryrun = True

    profiles = Profile.objects.all()

    for prof in collect_accountless(profiles):
      # ensure an email account is set
      if len(prof.email) == 0 or prof.email is None:
        print(".. Profile '%s %s' has no account, but no email address is set!" % (prof.first_name, prof.last_name))
        continue

      if not dryrun:
        print(".. Sending reset email to %s" % prof.email)
        send_reset_email(prof)
