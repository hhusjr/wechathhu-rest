# Generated by Django 3.0.2 on 2020-02-26 03:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0027_auto_20200226_0817'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ('name', 'id'), 'verbose_name': '系所', 'verbose_name_plural': '系所'},
        ),
    ]
