# Generated by Django 3.0.2 on 2020-02-12 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_auto_20200212_2154'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermeta',
            name='wechat',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
