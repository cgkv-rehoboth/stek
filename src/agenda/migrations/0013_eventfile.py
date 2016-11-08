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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=agenda.models.eventfilepath)),
                ('is_public', models.BooleanField(default=True)),
                ('event', models.ForeignKey(related_name='files', to='agenda.Event')),
                ('owner', models.ForeignKey(related_name='files', to='base.Profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
