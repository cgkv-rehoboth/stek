# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_family_thumbnail'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ('lastname', 'prefix')},
        ),
        migrations.AddField(
            model_name='family',
            name='gezinsaanhef',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='family',
            name='gezinsnr',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='family',
            name='is_active',
            field=models.NullBooleanField(default=True),
        ),
        migrations.AddField(
            model_name='family',
            name='prefix',
            field=models.CharField(blank=True, default='', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='belijdenisdatum',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='burgerstaat',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='doopdatum',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='geslacht',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='gvolgorde',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='huwdatum',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_active',
            field=models.NullBooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='lidnr',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='overlijdensdatum',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='soortlid',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='titel',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='voornamen',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role_in_family',
            field=models.CharField(choices=[('DAD', 'Vader'), ('MUM', 'Moeder'), ('KID', 'Kind'), ('IKI', 'Onafhankelijk kind')], default='KID', max_length=3, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='family',
            unique_together=set([('lastname', 'prefix', 'gezinsnr')]),
        ),
        migrations.AlterUniqueTogether(
            name='profile',
            unique_together=set([('first_name', 'initials', 'last_name', 'prefix', 'birthday', 'lidnr')]),
        ),
    ]
