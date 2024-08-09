from django.shortcuts import render
from django.http import HttpRequest
from auction.models import *
from auction.forms import *
from django.conf import settings
import stripe

# Create your views here.
def registration_view(request: HttpRequest):
    if request.method == "POST":
        form = Create_User_Form(request.POST)
        if form.is_valid():
            form.save()
            firstname = form.cleaned_data.get("first_name")
            lastname = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            name = f"{firstname} {lastname}"
            stripe.api_key = settings.STRIPE_KEY
            customer = stripe.Customer.create(
                name=name,
                email=email,
            )
    else:
        form = Create_User_Form()
    return render(request, "registration.html", {"form": form})