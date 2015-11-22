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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('live', livefield.fields.LiveField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('incalendar', models.BooleanField(default=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('startdatetime', models.DateTimeField()),
                ('enddatetime', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('repeatEvery', models.IntegerField(blank=True, default=None, null=True)),
                ('owner', models.ForeignKey(related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('minister', models.CharField(max_length=255)),
                ('theme', models.CharField(blank=True, max_length=255, default='')),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('comments', models.TextField(blank=True, null=True)),
                ('event', models.ForeignKey(related_name='duties', to='agenda.Event')),
                ('responsible', models.ForeignKey(related_name='duties', to=settings.AUTH_USER_MODEL)),
                ('timetable', models.ForeignKey(related_name='duties', to='agenda.Timetable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='service',
            name='timetable',
            field=models.ForeignKey(related_name='services', to='agenda.Timetable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='timetable',
            field=models.ForeignKey(related_name='events', to='agenda.Timetable'),
            preserve_default=True,
        ),
    ]
