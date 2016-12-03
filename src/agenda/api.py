from rest_framework.routers import DefaultRouter
from rest_framework import mixins, viewsets, filters, metadata
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.db.models import Q
from datetime import datetime, timedelta
from rest_framework import status
from time import strftime

from base.api import StekViewSet
from .models import *
from .serializers import *

class TeamViewSet(
    mixins.ListModelMixin,
    StekViewSet):

  model = Team
  queryset = Team.objects.all()
  serializer_class = TeamSerializer

class DutyViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        mixins.CreateModelMixin,
        StekViewSet):

  model = TimetableDuty
  queryset = TimetableDuty.objects.all()

  def get_serializer_class(self, *args, **kwargs):
    if self.request.method in ["POST", "PUT", "PATCH"]:
      return DutyWriteSerializer
    else:
      return DutyReadSerializer

class EventViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        mixins.CreateModelMixin,
        StekViewSet):

  model = Event
  queryset = Event.objects.select_related('timetable').all()
  serializer_class = EventSerializer

  def list(self, request):
    events = self.get_queryset()
    fromdate = request.GET.get('from')
    todate = request.GET.get('to')

    # filter events
    if fromdate is not None:
      fromdate = datetime.fromtimestamp(int(fromdate))
      events = events.filter(startdatetime__gte=fromdate)
    if todate is not None:
      todate = datetime.fromtimestamp(int(todate))
      events = events.filter(Q(enddatetime__lt=todate)|Q(enddatetime__isnull=True))

    return Response(self.get_serializer(events, many=True).data)

  def create(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(owner=request.profile)
    headers = self.get_success_headers(serializer.data)
    return Response(
      serializer.data,
      status=status.HTTP_201_CREATED,
      headers=headers)

class TimetableViewSet(mixins.ListModelMixin, StekViewSet):

  model = Timetable
  queryset = Timetable.objects.all()
  filter_fields = ("incalendar",)
  serializer_class = TimetableSerializer
  pagination_class = None


class ServiceViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        StekViewSet):

  model = Service
  serializer_class = ServiceSerializer

  # Get queryset to rerturn updated data on each request
  def get_queryset(self):
    if self.request.GET.get('reverseTime') == "true":
      return Service.objects.filter(enddatetime__lt=datetime.today().date()).order_by("-enddatetime", "-startdatetime")
    else:
      return Service.objects.filter(enddatetime__gte=datetime.today().date()).order_by("startdatetime", "enddatetime")


  def retrieve(self, request, *args, **kwargs):
    response = super().retrieve(request, *args, **kwargs)

    return response


  def list(self, request, *args, **kwargs):
    response = super().list(request, *args, **kwargs)

    if request.GET.get('reverseTime') == "true":
      temp = response.data['next']
      response.data['next'] = response.data['previous']
      response.data['previous'] = temp

    return response

  def create(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(owner=request.service)
    headers = self.get_success_headers(serializer.data)
    return Response(
      serializer.data,
      status=status.HTTP_201_CREATED,
      headers=headers)

router = DefaultRouter(trailing_slash=False)
router.register("duties", DutyViewSet, base_name="duties")
router.register("timetables", TimetableViewSet, base_name="timetable")
router.register("events", EventViewSet, base_name="events")
router.register("teams", TeamViewSet, base_name="teams")
router.register("services", ServiceViewSet, base_name="services")

urls = router.urls
