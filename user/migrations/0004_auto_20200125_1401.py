# Generated by Django 3.0.2 on 2020-01-25 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20200125_1155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='phone',
        ),
        migrations.AddField(
            model_name='user',
            name='wechat_open_id',
            field=models.CharField(default='a', max_length=255),
            preserve_default=False,
        ),
    ]
