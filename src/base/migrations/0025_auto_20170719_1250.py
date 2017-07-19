# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_remove_profile_role_in_family'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slide',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Slide',
        ),
    ]
