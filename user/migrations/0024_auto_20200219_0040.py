# Generated by Django 3.0.2 on 2020-02-18 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_auto_20200218_0218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='wechat_open_id',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True, verbose_name='微信openid'),
        ),
    ]