# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0005_MergeDutywithTimetable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='repeatEvery',
        ),
    ]
