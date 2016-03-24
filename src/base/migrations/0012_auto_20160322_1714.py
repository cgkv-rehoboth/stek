# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20160322_1701'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='profile',
            unique_together=set([('first_name', 'last_name'), ('email',)]),
        ),
    ]
