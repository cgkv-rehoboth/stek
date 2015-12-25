import os

from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.conf import settings

import base.views
import agenda.views
import agenda.api
import public.views

urlpatterns = patterns('',
  url(r'^', include(base.views.urls)),
  url(r'^', include(agenda.views.urls)),
  url(r'^', include(agenda.api.urls)),
  url(r'^', include(public.views.urls)),

  url(r'^admin/', include(admin.site.urls)),
  url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),

  url(r'^', include(static.static("/", document_root=os.path.join(settings.BASE_DIR, "static/")))),
)
