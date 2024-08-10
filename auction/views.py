from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
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
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=password)
            try:
                stripe.api_key = settings.STRIPE_KEY
                customer = stripe.Customer.create(
                    name=f"{firstname} {lastname}",
                    email=email,
                )
                bidder = Bidder.objects.create(
                    user=user,
                    stripe_id=customer.id
                )
            except:
                print("Can't create customer")
    else:
        form = Create_User_Form()
    return render(request, "registration.html", {"form": form})

def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Incorrect username and password combination")
    return render(request, "auction_login.html")

def testingView(req: HttpRequest) -> HttpResponse:
    stripe.api_key = settings.STRIPE_KEY
    customers = stripe.Customer.list()
    try:
        image = ItemImage.objects.get(id=1)
    except: 
        image = None
    
    return render(req, 'test.html', {'test': customers, 'image': image})

def productsTest(req: HttpRequest) -> HttpResponse:
    form = CreateAuctionItemForm()
    if req.method == 'POST':
        form = CreateAuctionItemForm(req.POST)
        if form.is_valid():
            newProduct = AuctionItem.objects.create(
                name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description'),
                starting_bid=form.cleaned_data.get('starting_bid'),
                current_bid=form.cleaned_data.get('starting_bid'),
                autobuy_price=form.cleaned_data.get('autobuy_price'),
                start_time=form.cleaned_data.get('start_time'),
                end_time=form.cleaned_data.get('end_time'),
            )
            print(newProduct)
            try:
                stripe.api_key = settings.STRIPE_KEY
                product = stripe.Product.create(
                    name=newProduct.name,
                    active=True,
                    description=newProduct.description,
                    metadata={}
                )
                print(product)
            except:
                print('something went wrong')
    return render(req, 'createProduct.html', {'form': form})

def imageTest(req: HttpRequest) -> HttpResponse:

    if req.method == 'POST':
        print(req.FILES)
        for file in req.FILES.getlist('images'):
            test = ItemImage.objects.create(file=file, item=AuctionItem.objects.get(id=1))
            print(test)
    return render(req, 'imgTest.html')

def displayItem(req: HttpRequest, id: int) -> HttpResponse:
    item = AuctionItem.objects.get(id=id)
    stripe.api_key = settings.STRIPE_KEY
    print(stripe.Product.list())
    return render(req, 'displayTest.html', {"item": item})
