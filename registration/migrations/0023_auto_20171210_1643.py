# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-10 21:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0022_families_workshops'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='photo_name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='photo name'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='workshop_one',
            field=models.ForeignKey(blank=None, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workshop_one', to='registration.Workshops'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='workshop_three',
            field=models.ForeignKey(blank=None, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workshop_three', to='registration.Workshops'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='workshop_two',
            field=models.ForeignKey(blank=None, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workshop_two', to='registration.Workshops'),
        ),
        migrations.AlterField(
            model_name='families',
            name='leader',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='time_paid',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='workshops',
            name='attendee_count',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='attendee count'),
        ),
    ]