# Generated by Django 2.2.5 on 2019-09-16 23:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textin', '0002_auto_20190916_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='end_date',
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='survey',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]