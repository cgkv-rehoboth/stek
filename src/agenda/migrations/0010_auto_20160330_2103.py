# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0009_ruilrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ruilrequest',
            name='timetableduty',
            field=models.ForeignKey(to='agenda.TimetableDuty', related_name='ruilen'),
        ),
        migrations.AlterField(
            model_name='ruilrequest',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='ruilen'),
        ),
        migrations.AlterUniqueTogether(
            name='ruilrequest',
            unique_together=set([('timetableduty', 'user')]),
        ),
    ]
