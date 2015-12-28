# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_ChangedProfileRelations'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='phone',
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
