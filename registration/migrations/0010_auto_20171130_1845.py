# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-30 23:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0009_auto_20171130_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conferencevars',
            name='alumni_attendee_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='conferencevars',
            name='early_attendee_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='conferencevars',
            name='regular_attendee_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='conferencevars',
            name='staff_attendee_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
