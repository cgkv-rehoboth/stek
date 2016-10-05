from django.core.management.base import BaseCommand, CommandError
from base.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
import unidecode

class NewAccountPasswordResetForm(PasswordResetForm):
  def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
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
    # create a new user and associate it with the profile
    user = User.objects.create_user(username=username, email=profile.email)
    profile.user = user
    profile.save()

    # init the password reset form
    reset_form = NewAccountPasswordResetForm({ "email": profile.email })
    if reset_form.is_valid():
      reset_form.save()
    else:
      print("[FAILURE]: Invalid password-reset-form for email '%s'" % profile.email)


class Command(BaseCommand):
  help = 'Create accounts for profiles without.'

  def add_arguments(self, parser):
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('--chosenones', action='store_true')

  def handle(self, *args, **options):
    dryrun = options['dryrun']
    chosenones = options['chosenones']
    if dryrun:
      print(">> Dry-run: only reporting")
      print()
      dryrun = True

    if chosenones:
      users = [
        #386, # André Jansen
        228, # Corné Mostert
        #145, # René van Bruggen
        #319, # Bram Steenbrink
        #130, # Willeke Boer-de Hoop
        #377, # Eric Reijm
        #196, # Max van der Stoel
        #366, # Anne Schouls
        #143, # Larissa van der Wal
      ]

      profiles = Profile.objects.filter(pk__in=users)
    else:
      profiles = Profile.objects.all()

    for prof in collect_accountless(profiles):
      # ensure an email account is set
      if prof.email is None or len(prof.email) == 0:
        print("[FAILURE] Profile '%s %s' has no account, but no email address is set!" % (prof.first_name, prof.last_name))
        continue

      ## think of a clever username
      # Remove all non alphabatic and special chars
      firstname = ''.join(e for e in unidecode.unidecode(prof.first_name.lower()) if e.isalnum())
      lastname = prof.last_name.split('-').pop()
      lastname = ''.join(e for e in unidecode.unidecode(lastname.lower()) if e.isalnum())

      # Merge it for an username
      username = "%s.%s" % (firstname, lastname)

      # ensure the username is not taken
      if User.objects.filter(username=username).exists():
        print("[FAILURE] Profile '%s %s' has no account, but the username '%s.%s' is taken." % (
          prof.first_name,
          prof.last_name,
          prof.first_name,
          prof.last_name
        ))
        continue

      print("[SUCCESS] Sending reset email to %s" % prof.email)
      if not dryrun:
        send_reset_email(prof, username)
