# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def load_roles(apps, schema_editor):

    from django.core.management import call_command

    call_command("loaddata", "teammemberroles")

def set_roles(apps, schema_editor):
    TeamMember = apps.get_model('agenda', 'TeamMember')

    for t in TeamMember.objects.all():
        t.role = 1
        t.save()

class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0011_user_to_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMemberRole',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=255)),
                ('short_name', models.CharField(max_length=4)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.RunPython(load_roles),
        migrations.RunPython(set_roles),
        migrations.AddField(
            model_name='teammember',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='role',
            field=models.ForeignKey(default=1, related_name='teammembers', to='agenda.TeamMemberRole'),
        ),
    ]
