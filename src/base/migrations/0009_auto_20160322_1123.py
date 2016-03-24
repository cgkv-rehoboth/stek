# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20160317_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wijk',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('naam', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='family',
            name='photo',
            field=models.FileField(upload_to=base.models.family_pic, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='wijk',
            field=models.ForeignKey(null=True, to='base.Wijk', blank=True),
        ),
    ]
