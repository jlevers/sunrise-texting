# Generated by Django 2.2.5 on 2019-09-18 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textin', '0004_auto_20190917_0633'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='end_message',
            field=models.CharField(default='That was the last question. Thank you for taking this survey!', max_length=500),
        ),
    ]
