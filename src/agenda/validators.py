import os
from django.core.exceptions import ValidationError


def validate_file_extension(file, extensions):
  # Get exetension by file name
  ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
  return ext.lower() in extensions

