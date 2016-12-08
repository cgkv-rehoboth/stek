# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_profile_has_logged_in'),
        ('agenda', '0013_eventfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='family',
            field=models.ForeignKey(blank=True, related_name='team_membership', to='base.Family', null=True),
        ),
        migrations.AddField(
            model_name='timetableduty',
            name='responsible_family',
            field=models.ForeignKey(blank=True, related_name='duties', to='base.Family', null=True),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='profile',
            field=models.ForeignKey(blank=True, related_name='team_membership', to='base.Profile', null=True),
        ),
        migrations.AlterField(
            model_name='timetableduty',
            name='responsible',
            field=models.ForeignKey(blank=True, related_name='duties', to='base.Profile', null=True),
        ),
    ]
