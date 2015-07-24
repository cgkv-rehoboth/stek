from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username', 'first_name', 'last_name', 'email')

class SimpleTimetableSerializer(serializers.ModelSerializer):
  """ Timetables without there events
  """
  owner = UserSerializer()

  class Meta:
    model = Timetable

class EventSerializer(serializers.ModelSerializer):
  owner = UserSerializer()
  timetable = SimpleTimetableSerializer()

  class Meta:
    model = Event

class TimetableSerializer(SimpleTimetableSerializer):
  """ Timetables with there events
  """

  events = EventSerializer(
    read_only=True,
    many=True
  )

  class Meta:
    model = Timetable

class SlideSerializer(serializers.ModelSerializer):
  owner = UserSerializer()

  class Meta:
    model = Slide

class ServiceSerializer(EventSerializer):
  class Meta:
    model = Service

class DutySerializer(EventSerializer):
  responsible = UserSerializer()

  class Meta:
    model = TimetableDuty
