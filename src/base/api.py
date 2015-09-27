from django.contrib.auth.models import User
from django.conf.urls import url, include

from rest_framework import routers, viewsets, views, response, permissions

from .routers import *
from .models import *
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()

  serializer_class = UserSerializer
'''
class TimetbleViewSet(viewsets.ModelViewSet):
  queryset = Timetable\
    .objects\
    .select_related('owner', 'events')\
    .all()

  serializer_class = TimetableSerializer
  filter_fields = ('title',)

class EventViewSet(viewsets.ModelViewSet):
  queryset = Event\
    .objects\
    .select_related('owner')\
    .all()

  serializer_class = EventSerializer
'''
class SlideViewSet(viewsets.ModelViewSet):
  queryset = Slide\
    .objects\
    .select_related('owner')\
    .all()

  serializer_class = SlideSerializer
'''
class DutyViewSet(viewsets.ModelViewSet):
  queryset = TimetableDuty\
    .objects\
    .select_related('timetable', 'responsible')\
    .all()

  serializer_class = DutySerializer
'''
router = AngularRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
'''router.register(r'events', EventViewSet)
router.register(r'timetables', TimetableViewSet)
router.register(r'duties', DutyViewSet)'''
router.register(r'slides', SlideViewSet)

urls = [
  url(r'^', include(router.urls)),
]
