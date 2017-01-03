# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0022_added_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 4, 12, 0, 0, 449859), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='modified_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 4, 12, 0, 0, 577752), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='family',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 4, 12, 0, 0, 353772), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='family',
            name='modified_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 4, 12, 0, 0, 729754), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 4, 12, 0, 0, 881863), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='modified_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 4, 12, 0, 0, 297854), auto_now=True),
            preserve_default=False,
        ),
    ]
