# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, primary_key=True, to='base.Event')),
                ('minister', models.CharField(max_length=255)),
                ('theme', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('base.event',),
        ),
        migrations.RemoveField(
            model_name='repeatedevent',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='repeatedevent',
            name='timetable',
        ),
        migrations.DeleteModel(
            name='RepeatedEvent',
        ),
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
        migrations.AddField(
            model_name='event',
            name='repeatEvery',
            field=models.IntegerField(blank=True, default=None, null=True),
            preserve_default=True,
        ),
    ]
