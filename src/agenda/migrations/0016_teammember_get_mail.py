# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0015_update_metaoptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='get_mail',
            field=models.BooleanField(default=True),
        ),
    ]
