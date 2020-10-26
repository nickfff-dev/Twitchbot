# Generated by Django 2.1.4 on 2019-01-01 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TwitchBot', '0002_auto_20190101_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='TwitchBot.SocialMediaAccount'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='bot',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='TwitchBot.TwitchBot'),
            preserve_default=False,
        ),
    ]