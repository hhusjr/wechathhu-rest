# Generated by Django 3.0.2 on 2020-01-29 04:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0010_auto_20200128_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='QRCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generated_key', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('label', models.CharField(max_length=32)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.Activity')),
            ],
            options={
                'unique_together': {('activity', 'label')},
            },
        ),
    ]
