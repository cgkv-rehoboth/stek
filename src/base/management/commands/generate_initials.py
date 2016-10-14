from django.core.management.base import BaseCommand, CommandError
from base.models import Profile

def collect_initialless(profiles):
    for prof in profiles:
        # check if user has an account
        if prof.initials is None or len(prof.initials) == 0:
            yield prof

class Command(BaseCommand):
  help = 'Generate initials for profiles without.'

  def add_arguments(self, parser):
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('profiles', nargs="*", default=[])

  def handle(self, *args, **options):
    dryrun = options['dryrun']
    profiles = options['profiles']
    if dryrun:
      print(">> Dry-run: only reporting")
      print()
      dryrun = True

    if len(profiles) > 0:
      profiles = Profile.objects.filter(pk__in=profiles)
      print(">> Only generating initials for:")
      for p in profiles:
        print(".. %s" % p.name)
      print()
    else:
      profiles = Profile.objects.all().order_by('last_name')

    for prof in collect_initialless(profiles):
      # ensure firstname is present
      if prof.first_name is None or len(prof.first_name) == 0:
        print("[FAILURE] Profile '%s' has no initial, but no first name is set!" % (prof.last_name))
        continue

      ## think of a clever initial
      i = ".".join(lt[0].upper() for lt in prof.first_name.split()) + "."

      print("[SUCCESS] Setting initials '%s' of %s %s" % (i, prof.first_name, prof.last_name))
      if not dryrun:
        prof.initials = i
        prof.save()