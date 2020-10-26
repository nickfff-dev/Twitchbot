# Generated by Django 2.1.4 on 2019-01-07 15:34

import TwitchBot.util
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TwitchBot', '0008_auto_20190102_1839'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twitchbot',
            name='period',
        ),
        migrations.AddField(
            model_name='twitchbot',
            name='priority',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='post',
            name='queued_time',
            field=models.DateField(default=TwitchBot.util.get_current_time),
        ),
        migrations.AlterField(
            model_name='twitchbot',
            name='created_after',
            field=models.DateField(default=TwitchBot.util.get_current_time),
        ),
    ]
