# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-30 02:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0035_auto_20171229_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialregcodes',
            name='code',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='special code'),
        ),
    ]
