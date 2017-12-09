# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-09 07:25
from __future__ import unicode_literals

import annoying.fields
from django.conf import settings
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0015_userinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='user_id',
            field=annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]