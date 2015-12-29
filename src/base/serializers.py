from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *

class FamilySerializer(serializers.ModelSerializer):
  class Meta:
    model = Family

class UserSerializer(serializers.ModelSerializer):

  class Meta:
    model = User
    fields = ('id', 'username', 'first_name', 'last_name', 'email')

class AddressSerializer(serializers.ModelSerializer):
  class Meta:
    model = Address

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
  owner = UserSerializer()
  favorite = UserSerializer()

  class Meta:
    model = Favorites