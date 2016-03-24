from django.contrib.auth.models import User, Group
from django.core.mail import send_mail

from rest_framework import serializers

from .models import *
from base.serializers import UserSerializer, RecaptchaField

class ContactSerializer(serializers.Serializer):
  email = serializers.EmailField()
  message = serializers.CharField()
  first_name = serializers.CharField()
  last_name = serializers.CharField()
  recaptcha = RecaptchaField()

  def save(self):
    sender = '%s %s' % (self.validated_data['first_name'], self.validated_data['first_name'])
    email = self.validated_data['email']
    to = ['test@cgkvwoerden.nl']
    message = self.validated_data['message']

    send_mail("Contactformulier: %s" % sender, message, email, to)

