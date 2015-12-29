from django.contrib.auth.models import User
from django.conf.urls import url, include

from rest_framework import routers, viewsets, views, response, permissions, metadata, mixins, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.routers import DefaultRouter

import django_filters

from .models import *
from .serializers import *

from rest_framework.permissions import IsAuthenticated

class MinimalMetadata(metadata.BaseMetadata):

  def determine_metadata(self, request, view):
    return dict(
      name=view.get_view_name(),
      description=view.get_view_description()
    )

class StekPaginator(PageNumberPagination):
  page_size = 100
  page_size_query_param = 'page_size'
  max_page_size = 1000

  def get_paginated_response(self, data):
    resp = super().get_paginated_response(data)

    # include the current page number
    resp.data['pageno'] = self.page.number

    return resp

class StekViewSet(viewsets.GenericViewSet):

  pagination_class = StekPaginator
  metadata_class = MinimalMetadata

  def get_serializer(self, *args, **kwargs):
    """ Improved get_serializer that will look for list_/detail_serializer_class properties
    """
    if self.__class__.serializer_class is not None:
      cls = self.__class__.serializer_class
    else:
      if self.action == 'list' and hasattr(self.__class__,
                           'list_serializer_class'):
        cls = self.__class__.list_serializer_class
      elif hasattr(self.__class__, 'detail_serializer_class'):
        cls = self.__class__.detail_serializer_class
      else:
        # error handling
        return super().get_serializer(*args, **kwargs)

    # default the context
    kwargs['context'] = self.get_serializer_context()

    return cls(*args, **kwargs)

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

class ProfileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, StekViewSet):

  queryset = Profile.objects.all()
  serializer_class = ProfileSerializer

  permission_classes = [IsAuthenticated]
  filter_backends = (filters.SearchFilter,)
  search_fields = ('user__first_name', 'user__last_name', 'user__email', 'address__street')

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
'''router.register(r'events', EventViewSet)
router.register(r'timetables', TimetableViewSet)
router.register(r'duties', DutyViewSet)'''
router.register(r'slides', SlideViewSet)

urls = router.urls

