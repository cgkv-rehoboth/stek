# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_addFavorite_addPhotos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='familymember',
            name='family',
        ),
        migrations.RemoveField(
            model_name='familymember',
            name='user',
        ),
        migrations.RemoveField(
            model_name='family',
            name='members',
        ),
        migrations.AddField(
            model_name='profile',
            name='family',
            field=models.ForeignKey(null=True, related_name='members', to='base.Family'),
        ),
        migrations.AddField(
            model_name='profile',
            name='role_in_family',
            field=models.CharField(max_length=3, null=True, choices=[('DAD', 'Father'), ('MUM', 'Mother'), ('KID', 'Kid'), ('IKI', 'Independent kid')], default='KID'),
        ),
        migrations.DeleteModel(
            name='FamilyMember',
        ),
    ]
