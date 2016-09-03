from django import forms

class UploadFileForm(forms.Form):
  file = forms.FileField(label='')

class UploadImageForm(forms.Form):
  file = forms.ImageField(label='')