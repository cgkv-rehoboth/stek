# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import livefield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('live', livefield.fields.LiveField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('incalendar', models.BooleanField(default=True)),
                ('title', models.CharField(blank=True, null=True, max_length=255)),
                ('startdatetime', models.DateTimeField()),
                ('enddatetime', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('repeatEvery', models.IntegerField(blank=True, null=True, default=None)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='events')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('minister', models.CharField(max_length=255)),
                ('theme', models.CharField(blank=True, default='', max_length=255)),
                ('comments', models.TextField(blank=True, null=True)),
                ('event', models.ForeignKey(to='agenda.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('live', livefield.fields.LiveField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimetableDuty',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('event', models.ForeignKey(to='agenda.Event', related_name='duties')),
                ('responsible', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='duties')),
                ('timetable', models.ForeignKey(to='agenda.Timetable', related_name='duties')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='service',
            name='timetable',
            field=models.ForeignKey(to='agenda.Timetable', related_name='services'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='timetable',
            field=models.ForeignKey(to='agenda.Timetable', related_name='events'),
            preserve_default=True,
        ),
    ]
