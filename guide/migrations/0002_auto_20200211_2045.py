# Generated by Django 3.0.2 on 2020-02-11 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guide',
            name='file',
            field=models.FileField(upload_to='guides'),
        ),
    ]
