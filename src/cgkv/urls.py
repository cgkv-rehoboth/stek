import os

from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, include, url, static
from django.views.generic import RedirectView
from django.views.static import serve
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from fiber.views import page

import base.views
import base.api
import agenda.views
import agenda.api
import public.views
import public.api
from .sitemaps import StaticViewSitemap

from machina.app import board

apipatterns = patterns('',
  url(r'', include(base.api.urls)),
  url(r'', include(public.api.urls)),
  url(r'^agenda/', include(agenda.api.urls)),
)

#@login_required
def media(request, path):
  # Check if the user is logged in OR if the user just wants to see the slide show
  if request.user.is_authenticated() or (path[0:7] == "slides/" or path[0:6] == "fiber/"):
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

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = patterns('',
  # App patterns
  url(r'^', include(base.views.urls)),
  url(r'^', include(agenda.views.urls)),
  url(r'^', include(public.views.urls)),

  url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

  url(r'^api/v1/', include(apipatterns)),
  url(r'^media/(?P<path>.*)$', media),

  # Fiber patterns
  url(r'^api/v2/', include('fiber.rest_api.urls')),
  url(r'^admin/fiber/', include('fiber.admin_urls')),
  # Fix the error that Fiber needs a trailing slash, by putting a trailing slash on everything that hasn't a trailing slash
  url(r'^admin/fiber/page/(?P<path>.+[^/])$', RedirectView.as_view(url='/admin/fiber/page/%(path)s/', permanent=False)),

  url(r'^admin$', RedirectView.as_view(url='admin/', permanent=True)),
  url(r'^admin/', include(admin.site.urls)),
  # url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),

  # url(r'^', include(static.static("/", document_root=os.path.join(settings.BASE_DIR, "static/")))),

  url(r'^markdown/', include('django_markdown.urls')),

  # Machina patterns
  url(r'^forum$', RedirectView.as_view(url='forum/', permanent=True), name='forum'),
  url(r'^forum/', include('custommachina.urls')),

  # Fiber patterns
  url(r'', page),
)
