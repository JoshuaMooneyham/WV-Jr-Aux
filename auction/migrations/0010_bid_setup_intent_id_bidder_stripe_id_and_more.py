# Generated by Django 5.0.7 on 2024-08-17 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0009_alter_auction_options_alter_auctionitem_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='setup_intent_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]