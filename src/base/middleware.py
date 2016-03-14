from base.models import *

class ProfileMiddleware(object):

  def process_request(self, request):
    if request.user.is_authenticated():
      try:
        request.profile = request.user.profile
      except Exception as e:
        request.profile = None
    else:
      request.profile = None

  def process_response(self, request, response):
    return response
