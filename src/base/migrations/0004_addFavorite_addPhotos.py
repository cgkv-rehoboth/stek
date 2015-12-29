# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0003_address_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('favorite', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='favorite_owner')),
            ],
        ),
        migrations.AddField(
            model_name='family',
            name='photo',
            field=models.FileField(null=True, blank=True, upload_to='/'),
        ),
        migrations.AddField(
            model_name='profile',
            name='photo',
            field=models.FileField(null=True, blank=True, upload_to='/'),
        ),
    ]
