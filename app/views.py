from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.conf import settings
import stripe

# Create your views here.
# print(settings.STRIPE_KEY)
def testingView(req: HttpRequest) -> HttpResponse:
    stripe.api_key = settings.STRIPE_KEY
    customers = stripe.Customer.list()
    
    return render(req, 'test.html', {'test': customers})
# # customer = stripe.Customer.retrieve("cus_Qayy8h85WAtWRo")
# # customer.delete()
# print(customers)