# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_add_initals'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='prefix',
            field=models.CharField(default='', null=True, max_length=64, blank=True),
        ),
    ]
