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
            name='EventFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=agenda.models.eventfilepath)),
                ('event', models.ForeignKey(to='agenda.Event', related_name='files')),
                ('owner', models.ForeignKey(to='base.Profile', related_name='files')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
