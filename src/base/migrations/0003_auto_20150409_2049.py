# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0002_auto_20150409_2002'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimetableDuty',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to='base.Event', parent_link=True)),
                ('responsible', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('base.event',),
        ),
        migrations.AddField(
            model_name='timetable',
            name='incalendar',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
