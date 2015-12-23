# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0002_AddTeams'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='team',
            name='email',
            field=models.EmailField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='timetable',
            name='team',
            field=models.ForeignKey(related_name='timetables', to='agenda.Team', null=True),
        ),
    ]
