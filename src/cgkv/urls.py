import os

from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.conf import settings

from base import views, api

urlpatterns = patterns('',
  url(r'^', include(views.urls)),

  url(r'^api/', include(
    api.urls
  )),

  url(r'^admin/', include(admin.site.urls)),
  url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),

  url(r'^', include(static.static("/", document_root=os.path.join(settings.BASE_DIR, "static/")))),
)
