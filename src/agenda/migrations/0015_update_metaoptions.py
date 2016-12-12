# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0014_add_family_to_team'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ('-startdatetime', '-enddatetime')},
        ),
        migrations.AlterModelOptions(
            name='eventfile',
            options={'ordering': ('-event__startdatetime', '-event__enddatetime', 'title')},
        ),
        migrations.AlterModelOptions(
            name='ruilrequest',
            options={'ordering': ('timetableduty',)},
        ),
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='teammember',
            options={'ordering': ('family__lastname', 'profile__last_name', 'team__name')},
        ),
        migrations.AlterModelOptions(
            name='teammemberrole',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='timetable',
            options={'ordering': ('title',)},
        ),
        migrations.AlterModelOptions(
            name='timetableduty',
            options={'ordering': ('-event__startdatetime', '-event__enddatetime', 'responsible_family__lastname', 'responsible__last_name')},
        ),
    ]
