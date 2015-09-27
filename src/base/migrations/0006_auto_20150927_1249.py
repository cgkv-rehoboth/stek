# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0005_auto_20150724_2140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='event',
            name='timetable',
        ),
        migrations.RemoveField(
            model_name='service',
            name='event_ptr',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.RemoveField(
            model_name='timetable',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Timetable',
        ),
        migrations.RemoveField(
            model_name='timetableduty',
            name='event_ptr',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.RemoveField(
            model_name='timetableduty',
            name='responsible',
        ),
        migrations.DeleteModel(
            name='TimetableDuty',
        ),
        migrations.RemoveField(
            model_name='familymember',
            name='profile',
        ),
        migrations.AddField(
            model_name='familymember',
            name='user',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='family',
            name='members',
            field=models.ManyToManyField(through='base.FamilyMember', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='familymember',
            name='role',
            field=models.CharField(default='KID', max_length=3, choices=[('DAD', 'Father'), ('MUM', 'Mother'), ('KID', 'Kid'), ('IKI', 'Independent kid')]),
        ),
    ]
