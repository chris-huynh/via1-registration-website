# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-28 01:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0033_auto_20171227_0105'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='vias_attended',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='VIA-1s attended'),
        ),
    ]