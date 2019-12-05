# Generated by Django 2.2.6 on 2019-10-09 00:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('textin', '0011_auto_20191006_2233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='responder',
            name='active_question',
        ),
        migrations.AddField(
            model_name='responder',
            name='active_survey',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='active_survey', to='textin.Survey'),
        ),
    ]