# Generated by Django 2.1.4 on 2019-01-02 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TwitchBot', '0007_auto_20190102_1810'),
    ]

    operations = [
        migrations.RenameField(
            model_name='twitchbot',
            old_name='start_at',
            new_name='created_after',
        ),
    ]
