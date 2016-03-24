# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20160322_2133'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='profile',
            unique_together=set([]),
        ),
    ]
