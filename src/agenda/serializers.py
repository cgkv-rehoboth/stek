from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
from base.serializers import UserSerializer

class TimetableSerializer(serializers.ModelSerializer):
  owner = UserSerializer()

  class Meta:
    model = Timetable

class ShortTimetableSerializer(serializers.ModelSerializer):
  """ Minimal timetable
  """

  class Meta:
    model = Timetable
    fields = ["pk", "title", "incalendar", "color"]

class EventSerializer(serializers.ModelSerializer):
  owner = UserSerializer()
  timetable = ShortTimetableSerializer()

  class Meta:
    model = Event

class TeamSerializer(serializers.ModelSerializer):
  members = UserSerializer(many=True)

  class Meta:
    model = Team

class EventWithDutiesSerializer(EventSerializer):

  class CustomDutySerializer(serializers.ModelSerializer):
    responsible = UserSerializer()

    class Meta:
      model = TimetableDuty
      fields = ['pk', 'responsible']

  duties = CustomDutySerializer(many=True)

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
