# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agenda', '0008_auto_20160324_2245'),
    ]

    operations = [
        migrations.CreateModel(
            name='RuilRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('comments', models.TextField(blank=True)),
                ('timetableduty', models.ForeignKey(to='agenda.TimetableDuty')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
