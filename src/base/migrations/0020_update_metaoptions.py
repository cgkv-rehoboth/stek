# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_profile_has_logged_in'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ('street', 'city')},
        ),
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ('lastname',)},
        ),
        migrations.AlterModelOptions(
            name='wijk',
            options={'ordering': ('id',)},
        ),
        migrations.AlterField(
            model_name='profile',
            name='address',
            field=models.ForeignKey(related_name='profile', null=True, blank=True, to='base.Address'),
        ),
    ]
