from base.api import StekViewSet
from .models import *
from .serializers import *
from rest_framework.routers import DefaultRouter
from rest_framework import mixins, viewsets, filters, metadata
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.db.models import Q
from datetime import datetime, timedelta

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

class TimetableViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        StekViewSet):

  model = Timetable
  queryset = Timetable.objects.all()
  filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
  filter_fields = ("incalendar",)
  serializer_class = TimetableSerializer

  def list(self, request, *args, **kwargs):
    # We use a custom implementation, because we need to filter the related (!) set of events
    # super().list does all filtering on the timetables + pagination for us though
    resp = super().list(request, *args, **kwargs)
    data = resp.data['results']

    pks = list(set([t['id'] for t in data]))
    events = Event.objects.select_related('timetable').filter(pk__in=pks)
    fromdate = request.GET.get('from')
    todate = request.GET.get('to')

    # filter events
    if fromdate is not None:
      events = events.filter(startdatetime__gte=datetime.fromtimestamp(int(fromdate)))
    if todate is not None:
      events = events.filter(enddatetime__lt=datetime.fromtimestamp(int(todate)))

    events_by_table = dict([ (pk, []) for pk in pks ])

    for e in events:
      events_by_table[e.timetable.pk].append(e)

    for i, x in enumerate(data):
      resp.data['results'][i]['events'] = \
        EventWithDutiesSerializer(events_by_table[x['id']], many=True).data

    return resp

router = DefaultRouter()
router.register("duties", DutyViewSet, base_name="duties")
router.register("timetables", TimetableViewSet, base_name="timetable")
router.register("events", EventViewSet, base_name="events")

urls = router.urls
