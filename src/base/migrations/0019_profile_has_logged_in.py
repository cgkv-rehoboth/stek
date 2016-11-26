# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_add_prefix'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='has_logged_in',
            field=models.NullBooleanField(default=False),
        ),
    ]
