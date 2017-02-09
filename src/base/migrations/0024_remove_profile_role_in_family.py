# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_added_timestampedmodels'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='role_in_family',
        ),
    ]
