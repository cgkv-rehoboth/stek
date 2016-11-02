from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UploadFileForm(forms.Form):
  file = forms.FileField(label='')

class UploadImageForm(forms.Form):
  file = forms.ImageField(label='')

class LoginForm(AuthenticationForm):
  username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'placeholder': 'Gebruikersnaam', 'autofocus': 'autofocus'}))
  password = forms.CharField(label="Wachtwoord", widget=forms.PasswordInput(attrs={'placeholder': 'Wachtwoord'}))