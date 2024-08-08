from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.conf import settings
import stripe
from auction.models import *

# Create your views here.
# print(settings.STRIPE_KEY)
def testingView(req: HttpRequest) -> HttpResponse:
    stripe.api_key = settings.STRIPE_KEY
    customers = stripe.Customer.list()
    image = ItemImages.objects.get()
    
    return render(req, 'test.html', {'test': customers, 'image': image})
# # customer = stripe.Customer.retrieve("cus_Qayy8h85WAtWRo")
# # customer.delete()
# print(customers)