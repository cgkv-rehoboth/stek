# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_family_reverse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorites',
            name='favorite',
            field=models.ForeignKey(related_name='favorited_by', to='base.Profile'),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='owner',
            field=models.ForeignKey(related_name='favorites', to='base.Profile'),
        ),
    ]
