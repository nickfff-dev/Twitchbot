# Generated by Django 2.1.4 on 2019-01-07 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TwitchBot', '0009_auto_20190107_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialmediaaccount',
            name='period',
            field=models.IntegerField(default=60),
        ),
    ]
