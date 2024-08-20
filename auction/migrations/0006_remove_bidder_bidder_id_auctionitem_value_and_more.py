# Generated by Django 5.0.7 on 2024-08-16 23:32

import django.db.models.deletion
import djmoney.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0005_bid_payment_intent_id_bidder_stripe_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bidder',
            name='bidder_id',
        ),
        migrations.AddField(
            model_name='auctionitem',
            name='value',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='auctionitem',
            name='auction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.auction'),
        ),
    ]