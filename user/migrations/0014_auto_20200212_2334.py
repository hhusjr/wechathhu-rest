# Generated by Django 3.0.2 on 2020-02-12 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_usermeta_wechat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermeta',
            name='department',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='usermeta',
            name='post',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
