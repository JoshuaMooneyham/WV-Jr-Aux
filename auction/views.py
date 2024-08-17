from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import stripe.error
from auction.models import *
from auction.forms import *
from django.conf import settings
import stripe, json, logging

logger = logging.getLogger(__name__)

import random
import datetime
import re

def generateBidderId() -> int:
    while True:
        num: int = random.randint(100000000, 999999999)
        if len(Bidder.objects.filter(bidder_id=num)) == 0:
            return num
        
# Create your views here.

# ============{ ITEM VIEWS }============ #

# ==={ Create Item }=== #

def createProduct(req: HttpRequest, auctionId: int) -> HttpResponse:
    form = CreateAuctionItemForm()
    if req.method == 'POST':
        form = CreateAuctionItemForm(req.POST)
        if form.is_valid():
            try:
                stripe.api_key = settings.STRIPE_KEY
                product = stripe.Product.create(
                    name=form.cleaned_data.get('name'),
                    active=True,
                    description=form.cleaned_data.get('description'),
                    metadata={}
                )
                price = stripe.Price.create(
                    currency="usd",
                    product=product.id,
                    unit_amount=form.cleaned_data.get('starting_bid'),
                )
                newProduct = AuctionItem.objects.create(
                    name=form.cleaned_data.get('name'),
                    active=True,
                    stripe_id=product.id,
                    description=form.cleaned_data.get('description'),
                    starting_bid=form.cleaned_data.get('starting_bid'),
                    current_bid=form.cleaned_data.get('starting_bid'),
                    autobuy_price=form.cleaned_data.get('autobuy_price'),
                    auction=Auction.objects.get(id=auctionId)
                )
                for file in req.FILES.getlist('images'):
                    ItemImage.objects.create(file=file, item=newProduct)
                return redirect("auctionFront", 1)
            except:
                print('something went wrong')
    return render(req, 'createProduct.html', {'form': form})

# ==={ Read Item }=== #

def displayItem(req: HttpRequest, auctionId:int, id: int) -> HttpResponse:
    item = AuctionItem.objects.get(id=id)
    images = [img for img in item.images.all()]

    if req.method == "POST":
        amount = req.POST.get('amount')
        stripe.api_key = settings.STRIPE_KEY  
        if amount != None and (int(amount) >= item.current_bid + 500):
            logger.debug("WORKING!!!!")
            bid = Bid(bidder=Bidder.objects.get(id=req.POST.get("bidder")), amount=int(amount), item=AuctionItem.objects.get(id=req.POST.get("item")), payment_intent_id=req.POST.get("setup_intent"))
            print(bid)
            bid.save()
            item.current_bid = int(amount)
            item.save()
    lowestAllowedBid = item.current_bid + 500
    payment_method_id = req.POST.get("selected_payment_method")
    logger.debug(f"Python Payment Method: {payment_method_id}")
    setup_intent = create_setup_intent(req, item.stripe_id, payment_method_id)
    saved_cards = list_payment_methods(req)

            
    return render(req, 'displayItem.html', {"item": item, "images": images, "lab": lowestAllowedBid, "setup_intent": setup_intent, "saved_cards": saved_cards, "STRIPE_TEST_PUBLIC_KEY": settings.STRIPE_TEST_PUBLIC_KEY, "auctionId": auctionId})

# ==={ Update Item }=== #

def updateItem(req: HttpRequest, auctionId: int, id: int) -> HttpResponse:

    return render(req, 'updateItem.html')

# ==={ Delete Item }=== #

def deleteItem(req: HttpRequest, auctionId: int, id: int) -> HttpResponse:
    item = AuctionItem.objects.get(id=id)
    stripe.api_key = settings.STRIPE_KEY
    try:
        stripe.Product.delete(item.stripe_id)
        item.delete()
    except:
        print("Something Happened while deleting")
    
    return redirect("auctionFront", auctionId)







# ============{ AUCTION VIEWS }============ #

# ==={ Create Auction }=== #

def createAuction(req: HttpRequest) -> HttpResponse:
    form = CreateAuctionForm()
    if req.method == 'POST':
        form = CreateAuctionForm(req.POST)
        print(req.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('auctionFront')
            except:
                print('Error Creating Auction')
                
    return render(req, 'createAuction.html', {"form": form})

# ==={ Display Auction }=== #

def auctionFront(req: HttpRequest, id: int) -> HttpResponse:
    context = {}

    auction = Auction.objects.get(id=id)
    context['auction'] = auction
    context["items"] = auction.auctionitem_set.all()
    end = re.sub('[-TZ:+]', " ", f'{auction.end_date}')
    es = end.split(" ")
    endTime = datetime.datetime(int(es[0]), int(es[1]), int(es[2]), int(es[3]), int(es[4]), int(es[5]))

    start = re.sub('[-TZ:+]', " ", f'{auction.start_date}')
    ss = start.split(" ")
    startTime = datetime.datetime(int(ss[0]), int(ss[1]), int(ss[2]), int(ss[3]), int(ss[4]), int(ss[5]))
    now = datetime.datetime.now()
    
    if now > endTime:
        context["over"] = True
        for item in auction.auctionitem_set.all():
            print(item.active)
            item.active = False
            item.save()
            print(item.active)
    elif now > startTime:
        left = endTime - now
        print(left)
        hours = (int(left.seconds) - int(left.seconds) % 3600) / 3600
        minutes = ((int(left.seconds) - hours * 3600) - int(left.seconds) % 60) / 60
        seconds = int(left.seconds) - (hours * 3600 + minutes * 60)
        hours += (int(left.days) * 86400) / 3600
        hourS = f'{hours:.0f}'
        minuteS = f'{minutes:.0f}'
        secondS = f'{seconds:.0f}'
        print(f'{hourS}:{minuteS}:{secondS}')
        context['left'] = f'{hourS if len(hourS) > 1 else "0"+hourS}:{minuteS if len(minuteS) > 1 else "0"+minuteS}:{secondS if len(secondS) > 1 else "0"+secondS}'
    else:
        context["notStarted"] = True

    return render(req, 'auctionFront.html', context)

# ==={ Update Auction }=== #

def viewAuctionsList(req: HttpRequest, id: int) -> HttpResponse:
    auctions = Auction.objects.all()


    return render(req, 'auctionList.html', {'auctions': auctions, 'id': id})







# ============{ USER AUTH VIEWS }============ #

# ==={ Register }=== #

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
                    stripe_id=customer.id,
                    bidder_id=generateBidderId()
                )

                if user.is_authenticated:
                    return redirect("/auction/login")
            except:
                print("Can't create customer")
    else:
        form = Create_User_Form()
    return render(request, "registration.html", {"form": form})

# ==={ Login }=== #

def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("add_payment_method")
        else:
            messages.error(request, "Incorrect username and password combination")
    return render(request, "auction_login.html")







# ============{ MICHAELS VIEWS }============ #

def add_payment_view(request: HttpRequest):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        
        logging.info(f'Received payment_method_id: {payment_method_id}')

        if not payment_method_id:
            return JsonResponse({'error': 'Payment Method ID is required'}, status=400)

        try:
            stripe.api_key = settings.STRIPE_KEY
            bidder = Bidder.objects.get(user=request.user)

            logging.info(bidder.stripe_id)

            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=bidder.stripe_id
            )

            stripe.Customer.modify(
                bidder.stripe_id,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                }
            )

            return JsonResponse({'success': True, 'customer_id': bidder.stripe_id})
        except:
            print("Invalid card")
    return render(request, "add_payment.html", {'STRIPE_TEST_PUBLIC_KEY': settings.STRIPE_TEST_PUBLIC_KEY})

def list_payment_methods(request: HttpRequest):
    bidder = Bidder.objects.get(user=request.user)
    payment_methods = stripe.PaymentMethod.list(
        customer=bidder.stripe_id,
        type="card",
    )
    return payment_methods

def payment_settings(request: HttpRequest):
    stripe.api_key = settings.STRIPE_KEY
    saved_cards = list_payment_methods(request)
    return render(request, "payment_settings.html", {"saved_cards": saved_cards})

def edit_payment_method(request: HttpRequest, payment_method_id):
    stripe.api_key = settings.STRIPE_KEY
    current_year = datetime.datetime.today().year
    month_list = [f"{month:02}" for month in range(1, 13)]
    year_list = range(current_year, current_year + 20)
    payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
    if request.method == "POST":
        stripe.PaymentMethod.modify(
            payment_method_id,
            card={
                "exp_month":request.POST.get("exp_month"),
                "exp_year":request.POST.get("exp_year"),
                }
            )
    return render(request, "edit_payment_method.html", {"card": payment_method, "month_list": month_list, "year_list": year_list})

def delete_payment_method(request: HttpRequest, payment_method_id):
    stripe.api_key = settings.STRIPE_KEY
    try:
        stripe.PaymentMethod.detach(payment_method_id)
    except:
        logger.debug("Can't remove")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_setup_intent(request: HttpRequest, product_id, payment_method_id):
    stripe.api_key = settings.STRIPE_KEY
    bidder = Bidder.objects.get(user=request.user)
    customer = stripe.Customer.retrieve(id=bidder.stripe_id)
    item = AuctionItem.objects.get(stripe_id=product_id)

    setup_intent = stripe.SetupIntent.create(
        customer=customer.id,
        payment_method=payment_method_id,
        payment_method_types=['card'],
        metadata={
            "product_id": product_id,
        }
    )
    return setup_intent

def end_auction(request: HttpRequest, product_id):
    stripe.api_key = settings.STRIPE_KEY
    item = AuctionItem.objects.get(stripe_id=product_id)
    highest_bid = Bid.objects.filter(item=item).order_by("-amount").first()
    logger.debug(highest_bid)
    setup_intent = stripe.SetupIntent.retrieve(highest_bid.payment_intent_id)
    logger.debug(f"Setup Intent: {setup_intent}")
    stripe.PaymentIntent.create(
        amount=item.current_bid,
        currency="usd",
        customer=highest_bid.bidder.stripe_id,
        payment_method=setup_intent.payment_method,
        automatic_payment_methods=
        {
            "enabled": True,
            "allow_redirects": "never",
        },
        confirm=True
    )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

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
            try:
                stripe.api_key = settings.STRIPE_KEY
                product = stripe.Product.create(
                    name=form.cleaned_data.get('name'),
                    active=True,
                    description=form.cleaned_data.get('description'),
                    metadata={}
                )
                newProduct = AuctionItem.objects.create(
                    name=form.cleaned_data.get('name'),
                    active=True,
                    stripe_id=product.id,
                    description=form.cleaned_data.get('description'),
                    starting_bid=form.cleaned_data.get('starting_bid'),
                    current_bid=form.cleaned_data.get('starting_bid'),
                    autobuy_price=form.cleaned_data.get('autobuy_price'),
                    auction=Auction.objects.get(id=1)
                )
                for file in req.FILES.getlist('images'):
                    ItemImage.objects.create(file=file, item=newProduct)
                return redirect("auctionFront")
            except:
                print('something went wrong')
    return render(req, 'createProduct.html', {'form': form})

def auctionFront(req: HttpRequest, id: int) -> HttpResponse:
    context = {}

    auction = Auction.objects.get(id=id)
    context['auction'] = auction
    context["items"] = auction.auctionitem_set.all()
    end = re.sub('[-TZ:+]', " ", f'{auction.end_date}')
    es = end.split(" ")
    endTime = datetime.datetime(int(es[0]), int(es[1]), int(es[2]), int(es[3]), int(es[4]), int(es[5]))

    start = re.sub('[-TZ:+]', " ", f'{auction.start_date}')
    ss = start.split(" ")
    startTime = datetime.datetime(int(ss[0]), int(ss[1]), int(ss[2]), int(ss[3]), int(ss[4]), int(ss[5]))
    now = datetime.datetime.now()
    
    if now > endTime:
        context["over"] = True
        for item in auction.auctionitem_set.all():
            print(item.active)
            item.active = False
            item.save()
            print(item.active)
    elif now > startTime:
        left = endTime - now
        print(left)
        hours = (int(left.seconds) - int(left.seconds) % 3600) / 3600
        minutes = ((int(left.seconds) - hours * 3600) - int(left.seconds) % 60) / 60
        seconds = int(left.seconds) - (hours * 3600 + minutes * 60)
        hours += (int(left.days) * 86400) / 3600
        hourS = f'{hours:.0f}'
        minuteS = f'{minutes:.0f}'
        secondS = f'{seconds:.0f}'
        print(f'{hourS}:{minuteS}:{secondS}')
        context['left'] = f'{hourS if len(hourS) > 1 else "0"+hourS}:{minuteS if len(minuteS) > 1 else "0"+minuteS}:{secondS if len(secondS) > 1 else "0"+secondS}'
    else:
        context["notStarted"] = True

    return render(req, 'auctionFront.html', context)

def displayItem(req: HttpRequest, id: int) -> HttpResponse:
    item = AuctionItem.objects.get(id=id)
    images = [img for img in item.images.all()]
    if req.method == "POST":
        amount = req.POST.get('amount')
        stripe.api_key = settings.STRIPE_KEY  
        if amount != None and (int(amount) >= item.current_bid + 500):
            logger.debug("WORKING!!!!")
            bid = Bid(bidder=Bidder.objects.get(id=req.POST.get("bidder")), amount=int(amount), item=AuctionItem.objects.get(id=req.POST.get("item")), payment_intent_id=req.POST.get("setup_intent"))
            print(bid)
            bid.save()
            item.current_bid = int(amount)
            item.save()
    lowestAllowedBid = item.current_bid + 500
    payment_method_id = req.POST.get("selected_payment_method")
    logger.debug(f"Python Payment Method: {payment_method_id}")
    setup_intent = create_setup_intent(req, item.stripe_id, payment_method_id)
    saved_cards = list_payment_methods(req)

            
    return render(req, 'displayItem.html', {"item": item, "images": images, "lab": lowestAllowedBid, "setup_intent": setup_intent, "saved_cards": saved_cards, "STRIPE_TEST_PUBLIC_KEY": settings.STRIPE_TEST_PUBLIC_KEY})

    # return render(req, 'displayItem.html', {"item": item, "images": images, "lab": lowestAllowedBid})

def deleteItem(req: HttpRequest, id: int) -> HttpResponse:
    item = AuctionItem.objects.get(id=id)
    stripe.api_key = settings.STRIPE_KEY
    try:
        stripe.Product.delete(item.stripe_id)
        item.delete()
    except:
        print("Something Happened while deleting")
    
    return redirect("auctionFront")

def createAuction(req: HttpRequest) -> HttpResponse:
    form = CreateAuctionForm()
    if req.method == 'POST':
        form = CreateAuctionForm(req.POST)
        print(req.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('auctionFront')
            except:
                print('Error Creating Auction')
                
    return render(req, 'createAuction.html', {"form": form})


