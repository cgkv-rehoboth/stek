from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
from base.serializers import ProfileSerializer

class TimetableSerializer(serializers.ModelSerializer):
  owner = ProfileSerializer()

  class Meta:
    model = Timetable

class ShortTimetableSerializer(serializers.ModelSerializer):
  """ Minimal timetable
  """

  class Meta:
    model = Timetable
    fields = ["pk", "title", "incalendar", "color"]

class EventSerializer(serializers.ModelSerializer):
  owner = ProfileSerializer()
  timetable = ShortTimetableSerializer()

  class Meta:
    model = Event
    read_only_fields = ["owner"]

class TeamSerializer(serializers.ModelSerializer):
  members = ProfileSerializer(many=True)

  class Meta:
    model = Team

class EventWithDutiesSerializer(EventSerializer):

  class CustomDutySerializer(serializers.ModelSerializer):
    responsible = ProfileSerializer()

    class Meta:
      model = TimetableDuty
      fields = ['pk', 'responsible']

  duties = CustomDutySerializer(many=True)

class ServiceSerializer(EventSerializer):
  class Meta:
    model = Service

class DutyReadSerializer(serializers.ModelSerializer):

  responsible = ProfileSerializer()
  event = EventSerializer()
  timetable = ShortTimetableSerializer()

  class Meta:
    model = TimetableDuty
    fields = ['pk', 'responsible', 'event', 'timetable', 'comments']

class DutyWriteSerializer(serializers.ModelSerializer):

  class Meta:
    model = TimetableDuty
    fields = ['pk', 'responsible', 'event', 'timetable', 'comments']
