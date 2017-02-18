from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from ckeditor.widgets import CKEditorWidget
from .models import *

class UploadEventFileForm(ModelForm):
  class Meta:
    model = EventFile
    fields = ('title', 'event', 'file', 'is_public')


class TeamForm(ModelForm):
  description = forms.CharField(widget=CKEditorWidget('email'))
  remindermail = forms.CharField(widget=CKEditorWidget('email'))

  class Meta:
    model = Team
    fields = ['name', 'email', 'description', 'remindermail']
