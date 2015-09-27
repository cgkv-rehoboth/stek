# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0007_delete_timetable_models'),
    ]

    operations = [
        migrations.DeleteModel('Timetable'),
        migrations.DeleteModel('Event'),
        migrations.DeleteModel('TimetableDuty'),
        migrations.DeleteModel('Service'),
    ]
