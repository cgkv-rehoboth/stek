from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
from base.serializers import UserSerializer, ProfileSerializer

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

class EventFileSerializer(serializers.ModelSerializer):

  class Meta:
    model = EventFile
    fields = ["pk", "title", "file", "type", "filesize", "is_public"]

class EventSerializer(serializers.ModelSerializer):
  title = serializers.CharField(min_length=5)
  description = serializers.CharField()
  files = EventFileSerializer(many=True, read_only=True)

  class Meta:
    model = Event
    fields = ["id", "title", "description", "startdatetime", "enddatetime", "files"]

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
  url = serializers.CharField()

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