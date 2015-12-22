# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import livefield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('live', livefield.fields.LiveField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('incalendar', models.BooleanField(default=True)),
                ('title', models.CharField(null=True, max_length=255, blank=True)),
                ('startdatetime', models.DateTimeField()),
                ('enddatetime', models.DateTimeField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('repeatEvery', models.IntegerField(null=True, default=None, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('live', livefield.fields.LiveField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimetableDuty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('comments', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('event_ptr', models.OneToOneField(to='agenda.Event', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
                ('minister', models.CharField(max_length=255)),
                ('theme', models.CharField(blank=True, max_length=255, default='')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('agenda.event',),
        ),
        migrations.AddField(
            model_name='timetableduty',
            name='event',
            field=models.ForeignKey(to='agenda.Event', related_name='duties'),
        ),
        migrations.AddField(
            model_name='timetableduty',
            name='responsible',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='duties'),
        ),
        migrations.AddField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='events'),
        ),
        migrations.AddField(
            model_name='event',
            name='timetable',
            field=models.ForeignKey(to='agenda.Timetable', related_name='events'),
        ),
    ]
