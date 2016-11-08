from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from .models import ServiceFile

class UploadServiceFileForm(ModelForm):
  class Meta:
    model = ServiceFile
    fields = ('title', 'service', 'file')

  # title = forms.CharField(label='Titel', max_length='255')
  # service = forms.ModelChoiceField(label='Dienst', queryset=ServiceFile.objects.all())
  # file = forms.FileField(label='Bestand')
