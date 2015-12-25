from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
from base.serializers import UserSerializer

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


class ShortTimetableSerializer(SimpleTimetableSerializer):
  """ Timetables without there events
  """

  class Meta:
    model = Timetable

class ServiceSerializer(EventSerializer):
  class Meta:
    model = Service

class DutyReadSerializer(serializers.ModelSerializer):

  responsible = UserSerializer()
  event = EventSerializer()
  timetable = ShortTimetableSerializer()

  class Meta:
    model = TimetableDuty
    fields = ['pk', 'responsible', 'event', 'timetable', 'comments']

class DutyWriteSerializer(serializers.ModelSerializer):

  class Meta:
    model = TimetableDuty
    fields = ['pk', 'responsible', 'event', 'timetable', 'comments']
