# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0016_teammember_get_mail'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='remindermail',
            field=models.TextField(blank=True),
        ),
    ]
