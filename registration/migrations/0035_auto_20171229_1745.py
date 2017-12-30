# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-29 22:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0034_userinfo_vias_attended'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialregcodes',
            name='code_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='code type'),
        ),
        migrations.AddField(
            model_name='specialregcodes',
            name='date_created',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='specialregcodes',
            name='date_expired',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='specialregcodes',
            name='method_of_payment',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='method of payment'),
        ),
    ]
