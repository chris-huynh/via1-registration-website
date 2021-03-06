# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-30 23:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0007_conferencevars'),
    ]

    operations = [
        migrations.AddField(
            model_name='conferencevars',
            name='staff_attendee_count',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='user',
            name='has_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='conferencevars',
            name='alumni_attendee_count',
            field=models.IntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='conferencevars',
            name='early_attendee_count',
            field=models.IntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='conferencevars',
            name='regular_attendee_count',
            field=models.IntegerField(default=None),
        ),
    ]
