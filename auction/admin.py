from django.contrib import admin
from auction.models import *

# Register your models here.
admin.site.register(Bidder)
admin.site.register(ItemImages)
admin.site.register(AuctionItem)
admin.site.register(Bid)