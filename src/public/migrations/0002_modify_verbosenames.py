# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='slide',
            options={'ordering': ('order',)},
        ),
        migrations.AlterField(
            model_name='slide',
            name='description',
            field=models.TextField(null=True, verbose_name='Beschrijving', blank=True),
        ),
        migrations.AlterField(
            model_name='slide',
            name='image',
            field=models.ImageField(upload_to='slides', verbose_name='Afbeelding'),
        ),
        migrations.AlterField(
            model_name='slide',
            name='order',
            field=models.IntegerField(verbose_name='Volgorde'),
        ),
        migrations.AlterField(
            model_name='slide',
            name='owner',
            field=models.ForeignKey(to='base.Profile', verbose_name='Eigenaar'),
        ),
        migrations.AlterField(
            model_name='slide',
            name='showtext',
            field=models.BooleanField(default=False, verbose_name='Tekst weergeven'),
        ),
        migrations.AlterField(
            model_name='slide',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Titel'),
        ),
    ]
