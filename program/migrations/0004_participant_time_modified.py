# Generated by Django 2.1 on 2018-08-12 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0003_auto_20180810_0854'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='time_modified',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
