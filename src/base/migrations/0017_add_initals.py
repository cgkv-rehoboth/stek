# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_auto_20160322_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='initials',
            field=models.CharField(blank=True, null=True, default='', max_length=64),
        ),
        migrations.AlterField(
            model_name='family',
            name='address',
            field=models.OneToOneField(blank=True, null=True, to='base.Address', related_name='family'),
        ),
    ]
