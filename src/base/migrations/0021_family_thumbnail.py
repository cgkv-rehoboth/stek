# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_update_metaoptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='thumbnail',
            field=models.FileField(blank=True, upload_to=base.models.family_pic_thumb, null=True),
        ),
    ]
