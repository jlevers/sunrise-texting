# Generated by Django 2.2.6 on 2019-10-02 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('textin', '0006_auto_20191001_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='complete_responder',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='survey',
            name='followup',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='textin.Survey'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
