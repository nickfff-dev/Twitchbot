# Generated by Django 2.1.5 on 2019-01-12 02:17

import TwitchBot.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TwitchBot', '0010_socialmediaaccount_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmediaaccount',
            name='period',
            field=TwitchBot.models.IntegerRangeField(),
        ),
    ]