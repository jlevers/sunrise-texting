# Generated by Django 2.2.6 on 2019-10-10 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textin', '0012_auto_20191009_0032'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='pushable',
            field=models.BooleanField(default=False),
        ),
    ]