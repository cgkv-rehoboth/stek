# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0006_remove_event_repeatevery'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='incalendar',
            field=models.BooleanField(default=True),
        ),
    ]
