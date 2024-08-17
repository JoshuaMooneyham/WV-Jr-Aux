from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Auction(models.Model):
    name = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Auction: {self.name}'
    
    class Meta: 
        ordering = ['-id']

class Bidder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="bidder_info")
    stripe_id = models.TextField()
    bidder_id = models.CharField(max_length=9, unique=True)

    def __str__(self) -> str:
        return f'Bidder: {self.bidder_id}'

class AuctionItem(models.Model):
    name = models.TextField()
    active = models.BooleanField()
    stripe_id = models.TextField()
    description = models.TextField()
    starting_bid = models.IntegerField(default=100) #Cents, base 100
    current_bid = models.IntegerField() #Cents, base 100
    value = models.IntegerField() #Cents, base 100
    autobuy_price = models.IntegerField(null=True, blank=True) #Cents, base 100
    highest_bidder = models.ForeignKey(Bidder, null=True, on_delete=models.SET_NULL, related_name='highest_bids')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'Product: {self.name}'
    
    class Meta:
        ordering = ['id']

class ItemImage(models.Model):
    file = models.ImageField(upload_to="")
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name='images')

    def __str__(self) -> str:
        return f'{self.item.name} Image: {self.file.name}'
    
    class Meta:
        ordering = ['id']


class Bid(models.Model):
    bidder = models.ForeignKey(Bidder, on_delete=models.CASCADE)
    amount = models.IntegerField() #Cents, base 100
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE)
    payment_intent_id = models.TextField(null=True, blank=True)
    setup_intent_id = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Bid from {self.bidder.bidder_id} on {self.item.name}'
    
    class Meta:
        ordering = ['-amount']