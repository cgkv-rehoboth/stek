from django.conf.urls import url, include
from rest_framework import routers

class AngularRouter(routers.DefaultRouter):
  routes = [
    routers.Route(
      url=r'^{prefix}/{lookup}{trailing_slash}$',
      mapping={
        'post': 'update',
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
      },
      name='{basename}-ng-update',
      initkwargs={'suffix': 'Instance'}
    )
  ] + routers.DefaultRouter.routes
