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
def home(request):
    return render(request, 'home.html')

def aboutUs(request):
    return render(request, 'about.html')

def projectsPage(request):
    return render(request, 'projects.html')

def contactUs(request):
    return render(request, 'contactus.html')

def loginPage(request):
    return render(request, 'login.html')

def logoutUser(request):
    return render(request, 'logout.html')