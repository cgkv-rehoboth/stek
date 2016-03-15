from django.contrib.auth.models import User
from django.conf.urls import url, include

from rest_framework import routers, viewsets, views, response, permissions, metadata, mixins, filters
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.routers import DefaultRouter
from rest_framework import status

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

class ProfileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, StekViewSet):

  class FavoriteFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
      if request.GET.get('favorites_only') is not None:
        return queryset.filter(favorited_by__owner=request.profile)
      else:
        return queryset

  queryset = Profile.objects.all()
  serializer_class = ProfileSerializer

  permission_classes = [IsAuthenticated]
  filter_backends = (FavoriteFilterBackend, filters.SearchFilter, filters.DjangoFilterBackend)
  search_fields = ('user__first_name', 'user__last_name', 'user__email', 'address__street')

  def retrieve(self, request, *args, **kwargs):
    response = super().retrieve(request, *args, **kwargs)
    response.data["is_favorite"] = self.get_object().is_favorite_for(request.profile)

    return response

  def list(self, request, *args, **kwargs):
    response = super().list(request, *args, **kwargs)

    is_favorite = dict(
      [ (v.favorite.pk, True) for v in Favorites.objects.filter(owner=request.profile) ])
    
    for i , u in enumerate(response.data['results']):
      response.data['results'][i]["is_favorite"] = is_favorite.get(u['id'], False)

    return response

  @detail_route(methods=['post'])
  def favorite(self, request, pk):
    fav = Favorites.objects.create(favorite=self.get_object(), owner=request.profile)
    ser = FavoriteSerializer(fav)
    return Response(ser.data, status=status.HTTP_201_CREATED)

  @detail_route(methods=['post'])
  def defavorite(self, request, pk):
    fav = Favorites.objects.filter(favorite=self.get_object(), owner=request.profile)
    fav.delete()

    return Response(status=status.HTTP_200_OK)

class FavoriteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, StekViewSet):
  queryset = Favorites.objects.all()
  serializer_class = FavoriteSerializer

  permission_classes = [IsAuthenticated]

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'favorites', FavoriteViewSet)

urls = router.urls
