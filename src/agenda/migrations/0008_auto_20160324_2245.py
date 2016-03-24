# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0007_timetable_incalendar'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='color',
            field=models.CharField(max_length=6, default='268bd2'),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='role',
            field=models.CharField(choices=[('LEI', 'leiding'), ('LID', 'lid')], max_length=3, default='LID'),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(related_name='teammembers', to='agenda.Team'),
        ),
    ]
