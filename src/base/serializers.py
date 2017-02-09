from django.contrib.auth.models import User, Group
from django.conf import settings
from rest_framework import serializers
from .models import *

from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

class Recaptcha(object):
  def __init__(self, resp, http_resp, valid):
    self.resp = resp
    self.http_resp = http_resp
    self.valid = valid

class RecaptchaField(serializers.Field):

  def to_representation(self, obj):
    return obj.http_resp

  def to_internal_value(self, data):
    params = urlencode({
      'secret': settings.RECAPTCHA_PRIVATE_KEY, 
      'response': data
    }).encode('utf-8')

    req = Request(
      url="https://www.google.com/recaptcha/api/siteverify",
      data=params,
      headers={
        'Content-type': 'application/x-www-form-urlencoded',
        'User-agent': 'reCAPTCHA Django'
      }
    )
    resp = urlopen(req)

    resp_data = json.loads(resp.read().decode('utf-8'))
    return_code = resp_data['success']

    if not return_code:
      raise serializers.ValidationError('Ongeldige Captcha')

    return Recaptcha(resp, resp_data, return_code)

class WijkSerializer(serializers.ModelSerializer):

  class Meta:
    model = Wijk

class AddressSerializer(serializers.ModelSerializer):
  wijk = WijkSerializer()

  class Meta:
    model = Address

class FamilyProfileSerializer(serializers.ModelSerializer):

  class Meta:
    model = Profile
    fields = ('id', 'first_name', 'initials', 'last_name', 'prefix', 'gvolgorde')

class FamilySerializer(serializers.ModelSerializer):
  address = AddressSerializer()
  members = FamilyProfileSerializer(many=True, read_only=True)

  class Meta:
    model = Family
    fields = ('id', 'lastname', 'prefix', 'photo', 'address', 'members', 'name_initials')

class UserSerializer(serializers.ModelSerializer):

  class Meta:
    model = User
    fields = ('id', 'username', 'first_name', 'last_name', 'email')

class ProfileSerializer(serializers.ModelSerializer):
  user = UserSerializer()
  address = AddressSerializer()
  family = FamilySerializer()

  class Meta:
    model = Profile

class SlideSerializer(serializers.ModelSerializer):
  owner = UserSerializer()

  class Meta:
    model = Slide

class FavoriteSerializer(serializers.ModelSerializer):
  owner = ProfileSerializer()
  favorite = ProfileSerializer()

  class Meta:
    model = Favorites