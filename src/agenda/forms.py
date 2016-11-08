from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from .models import EventFile

class UploadEventFileForm(ModelForm):
  class Meta:
    model = EventFile
    fields = ('title', 'event', 'file')

