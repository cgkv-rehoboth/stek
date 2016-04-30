# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0010_auto_20160330_2103'),
    ]

    operations = [
        migrations.RenameField(
            model_name='RuilRequest',
            old_name='user',
            new_name='profile',
        ),
        migrations.RenameField(
            model_name='TeamMember',
            old_name='user',
            new_name='profile',
        ),
    ]
