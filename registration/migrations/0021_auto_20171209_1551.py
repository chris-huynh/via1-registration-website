# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-09 20:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0020_auto_20171209_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='grad_year',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='graduation year'),
        ),
    ]
