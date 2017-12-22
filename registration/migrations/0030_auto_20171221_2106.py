# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-22 02:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0029_auto_20171214_0129'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialRegCodes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=10, null=True, verbose_name='special code')),
                ('usages_left', models.IntegerField(default=0, null=True, verbose_name='number of usages left')),
                ('includes_hotel', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='userinfo',
            name='family',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='registration.Families'),
        ),
        migrations.AddField(
            model_name='workshops',
            name='presenter',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='presenter name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Has no usage right now.', verbose_name='staff status'),
        ),
    ]
