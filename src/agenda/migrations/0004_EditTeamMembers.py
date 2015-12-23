# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0003_EditTeam'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(related_name='members', through='agenda.TeamMember', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='role',
            field=models.CharField(choices=[('LEI', 'Leiding'), ('LID', 'Lid')], default='LID', max_length=3),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='user',
            field=models.ForeignKey(related_name='team_membership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='team',
            field=models.ForeignKey(related_name='timetables', null=True, blank=True, to='agenda.Team'),
        ),
    ]
