from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Bidder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = "bidder_info")
    bidder_id = models.IntegerField(null=True, blank=True)
    stripe_id = models.CharField(max_length=50, null=True, blank=True)

class ItemImages(models.Model):
    file = models.ImageField(upload_to="", blank=True, null=True)

class AuctionItem(models.Model):
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    starting_bid = models.IntegerField(null=True, blank=True) #Cents, base 1000
    current_bid = models.IntegerField(null=True, blank=True) #Cents, base 1000
    autobuy_price = models.IntegerField(null=True, blank=True) #Cents, base 1000
    highest_bidder = models.ForeignKey(Bidder, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    images = models.ForeignKey(ItemImages, null=True, blank=True, on_delete=models.SET_NULL)

    
class Bid(models.Model):
    bidder = models.ForeignKey(Bidder, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True) #Cents, base 1000
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE)