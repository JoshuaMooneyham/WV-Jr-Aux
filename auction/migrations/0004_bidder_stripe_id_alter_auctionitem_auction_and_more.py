# Generated by Django 5.0.7 on 2024-08-10 14:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0003_auction_remove_auctionitem_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionitem',
            name='auction',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='auction.auction'),
        ),
        migrations.AlterField(
            model_name='bidder',
            name='bidder_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
