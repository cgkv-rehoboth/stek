from django.contrib import admin
from .models import *

admin.site.register(Timetable)
admin.site.register(Event)
admin.site.register(TimetableDuty)
admin.site.register(Service)