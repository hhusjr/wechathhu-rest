# Generated by Django 3.0.2 on 2020-02-18 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0007_auto_20200218_0124'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='meetingroom',
            options={'ordering': ('name', '-id'), 'verbose_name': '会议室', 'verbose_name_plural': '会议室'},
        ),
    ]
