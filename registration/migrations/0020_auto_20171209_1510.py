# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-09 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0019_auto_20171209_0315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='birth_date',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='birth date'),
        ),
    ]
