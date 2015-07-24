# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_address_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('lastname', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FamilyMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('role', models.CharField(choices=[('DAD', 'Father'), ('MUM', 'Mother'), ('KID', 'Kid')], max_length=3, default='KID')),
                ('family', models.ForeignKey(to='base.Family')),
                ('profile', models.ForeignKey(to='base.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='family',
            name='members',
            field=models.ManyToManyField(to='base.Profile', through='base.FamilyMember'),
            preserve_default=True,
        ),
    ]
