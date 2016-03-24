# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_family_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(upload_to=base.models.user_profile_pic, blank=True, null=True),
        ),
    ]
