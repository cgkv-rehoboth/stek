from base.api import StekViewSet
from .models import *
from .serializers import *
from rest_framework.routers import DefaultRouter
from rest_framework import mixins, viewsets, filters, metadata

class DutyViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        mixins.CreateModelMixin,
        StekViewSet):

  model = TimetableDuty
  queryset = TimetableDuty.objects.all()

  def get_serializer_class(self, *args, **kwargs):
    if self.request.method in ["POST", "PUT", "PATCH"]:
      return DutyWriteSerializer
    else:
      return DutyReadSerializer

router = DefaultRouter()
router.register("duties", DutyViewSet, base_name="duties")

urls = router.urls
