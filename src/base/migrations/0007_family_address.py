# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_favorite_to_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='address',
            field=models.OneToOneField(null=True, blank=True, to='base.Address'),
        ),
    ]
