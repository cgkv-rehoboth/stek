import os

from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, include, url, static
from django.views.static import serve
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse

import base.views
import base.api
import agenda.views
import agenda.api
import public.views
import public.api

apipatterns = patterns('',
  url(r'', include(base.api.urls)),
  url(r'', include(public.api.urls)),
  url(r'^agenda/', include(agenda.api.urls)),
)

@login_required
def media(request, path):
  if settings.DEBUG:
    dire = os.path.join(settings.MEDIA_ROOT, os.path.dirname(path))
    return serve(request, os.path.basename(path), dire)
  else:
    # use nginx x-accel-redirect
    # this allows us to serve the file directly using nginx,
    # but authenticate the user here
    url = os.path.join("/media-protected", path)
    response = HttpResponse()
    response['X-Accel-Redirect'] = url.encode('utf-8')

    return response

urlpatterns = patterns('',
  url(r'^', include(base.views.urls)),
  url(r'^', include(agenda.views.urls)),
  url(r'^', include(public.views.urls)),

  url(r'^api/v1/', include(apipatterns)),
  url(r'^media/(?P<path>.*)$', media),

  url(r'^admin/', include(admin.site.urls)),
  # url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),

  # url(r'^', include(static.static("/", document_root=os.path.join(settings.BASE_DIR, "static/")))),
)
