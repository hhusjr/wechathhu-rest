# Generated by Django 3.0.2 on 2020-02-10 07:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activity', '0011_qrcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClockinMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generated_key', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('label', models.CharField(max_length=32)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.Activity')),
            ],
            options={
                'unique_together': {('activity', 'label')},
            },
        ),
        migrations.CreateModel(
            name='ClockinRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('clockin_meta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.ClockinMeta')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
                'unique_together': {('user', 'clockin_meta')},
            },
        ),
        migrations.DeleteModel(
            name='QRCode',
        ),
    ]
