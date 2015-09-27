from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username', 'first_name', 'last_name', 'email')

class SlideSerializer(serializers.ModelSerializer):
  owner = UserSerializer()

  class Meta:
    model = Slide