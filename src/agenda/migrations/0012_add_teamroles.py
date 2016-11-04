# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0011_user_to_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='role',
            field=models.CharField(max_length=3, default='LID', choices=[('AMB', 'Ambetlijk scriba GKv-kerkverband'), ('VOO', 'Voorzitter'), ('JEU', 'Jeugdouderling'), ('LID', 'Lid'), ('LEI', 'Leiding'), ('SEC', 'Secretaris'), ('SEV', 'Secretaresse'), ('PEN', 'Penningmeester'), ('CCV', 'Contactpersoon CvB'), ('CBE', 'Contactpersoon beamer, geluid, muziek'), ('CKE', 'Contactpersoon kerkenraad'), ('CCA', 'Contactpersoon catechese'), ('CKI', 'Contactpersoon kinderkring'), ('CJE', 'Contactpersoon jeugdverenigingen'), ('CON', 'Contactpersoon'), ('ALA', 'Algemeen adjunct'), ('VKE', 'Vertegenwoordiger kerkenraad'), ('ADM', 'Administrateur'), ('BOE', 'Boekhouder'), ('SCR', 'Scriba')]),
        ),
    ]
