# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0004_EditTeamMembers'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetableduty',
            name='timetable',
            field=models.ForeignKey(related_name='duties', default=1, to='agenda.Timetable'),
            preserve_default=False,
        ),
    ]
