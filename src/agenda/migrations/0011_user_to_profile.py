# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_auto_20160322_2136'),
        ('agenda', '0010_auto_20160330_2103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teammember',
            name='user',
        ),
        migrations.AddField(
            model_name='ruilrequest',
            name='profile',
            field=models.ForeignKey(related_name='ruilen', to='base.Profile', default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teammember',
            name='profile',
            field=models.ForeignKey(related_name='team_membership', to='base.Profile', default=-1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(to='base.Profile', related_name='events'),
        ),
        migrations.AlterField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(through='agenda.TeamMember', to='base.Profile', related_name='members'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='owner',
            field=models.ForeignKey(to='base.Profile'),
        ),
        migrations.AlterField(
            model_name='timetableduty',
            name='responsible',
            field=models.ForeignKey(to='base.Profile', related_name='duties'),
        ),
        migrations.AlterUniqueTogether(
            name='ruilrequest',
            unique_together=set([('timetableduty', 'profile')]),
        ),
        migrations.RemoveField(
            model_name='ruilrequest',
            name='user',
        ),
    ]
