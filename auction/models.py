from django.db import models
from django.contrib.auth.models import User
import random

# Create your models here.
class Bidder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="bidder_info")
    bidder_id = models.IntegerField(unique=True)

class AuctionItem(models.Model):
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    starting_bid = models.IntegerField(default=100) #Cents, base 1000
    current_bid = models.IntegerField() #Cents, base 1000
    autobuy_price = models.IntegerField(null=True, blank=True) #Cents, base 1000
    highest_bidder = models.ForeignKey(Bidder, null=True, on_delete=models.SET_NULL, related_name='highest_bids')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class ItemImage(models.Model):
    file = models.ImageField(upload_to="")
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name='images')


class Bid(models.Model):
    bidder = models.ForeignKey(Bidder, on_delete=models.CASCADE)
    amount = models.IntegerField() #Cents, base 1000
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE)