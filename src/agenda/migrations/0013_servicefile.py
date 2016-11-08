# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import agenda.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_add_prefix'),
        ('agenda', '0012_add_teammemberrole_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceFile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=agenda.models.servicefilepath)),
                ('owner', models.ForeignKey(to='base.Profile', related_name='files')),
                ('service', models.ForeignKey(to='agenda.Service', related_name='files')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
