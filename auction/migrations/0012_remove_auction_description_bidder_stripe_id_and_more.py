# Generated by Django 5.0.7 on 2024-08-18 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0011_auctionitem_runner_up_bidder_stripe_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='description',
        ),
    ]
