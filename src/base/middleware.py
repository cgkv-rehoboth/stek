from base.models import *

class ProfileMiddleware(object):

  def process_request(self, request):
    if request.user.is_authenticated():
      request.profile = request.user.profile
    else:
      request.profile = None

  def process_response(self, request, response):
    return response
