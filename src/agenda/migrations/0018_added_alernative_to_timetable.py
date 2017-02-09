# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0017_team_remindermail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetable',
            name='owner',
            field=models.ForeignKey(related_name='timetables', to='base.Profile'),
        ),
    ]
