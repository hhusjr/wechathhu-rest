# Generated by Django 3.0.2 on 2020-02-17 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0022_auto_20200218_0124'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('username', 'id'), 'verbose_name': '教师用户', 'verbose_name_plural': '教师用户'},
        ),
    ]