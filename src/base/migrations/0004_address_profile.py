# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0003_auto_20150409_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('street', models.CharField(blank=True, max_length=255)),
                ('zip', models.CharField(blank=True, max_length=6)),
                ('city', models.CharField(blank=True, max_length=255)),
                ('country', models.CharField(max_length=255, default='Nederland')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('birthday', models.DateField()),
                ('address', models.ForeignKey(blank=True, null=True, to='base.Address')),
                ('user', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
