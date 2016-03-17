from django.conf.urls import patterns, include, url

from public.serializers import ContactSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def contact_post(request):
  serializer = ContactSerializer(data=request.data)

  if serializer.is_valid():
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
  else:
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

urls = [
  url(r'^contact/$', contact_post, name='contact-post'),
]
