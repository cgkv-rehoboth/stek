# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0025_auto_20170719_1250'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('image', models.ImageField(upload_to='slides')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('order', models.IntegerField()),
                ('showtext', models.BooleanField(default=False)),
                ('live', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(to='base.Profile')),
            ],
        ),
    ]
