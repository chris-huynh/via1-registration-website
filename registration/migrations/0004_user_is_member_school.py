# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-25 20:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_user_email_confirmed'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_member_school',
            field=models.BooleanField(default=False),
        ),
    ]
