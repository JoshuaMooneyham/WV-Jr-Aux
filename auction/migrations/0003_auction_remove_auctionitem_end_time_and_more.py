# Generated by Django 5.0.7 on 2024-08-10 14:08

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0002_alter_bidder_bidder_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='auctionitem',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='auctionitem',
            name='start_time',
        ),
        migrations.AddField(
            model_name='auctionitem',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='auctionitem',
            name='stripe_id',
            field=models.TextField(default="test"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='auctionitem',
            name='description',
            field=models.TextField(default="test"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bidder',
            name='bidder_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AddField(
            model_name='auctionitem',
            name='auction',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='auction.auction'),
        ),
    ]