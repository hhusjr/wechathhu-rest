# Generated by Django 3.0.2 on 2020-02-09 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0003_auto_20200209_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
