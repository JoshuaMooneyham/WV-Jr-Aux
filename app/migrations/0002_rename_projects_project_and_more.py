# Generated by Django 5.0.7 on 2024-08-07 01:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Projects',
            new_name='Project',
        ),
        migrations.RenameModel(
            old_name='UpcomingEvents',
            new_name='UpcomingEvent',
        ),
    ]
