from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, update_session_auth_hash
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

# def generateBidderId() -> int:
#     while True:
#         num: int = random.randint(100000000, 999999999)
#         if len(Bidder.objects.filter(bidder_id=num)) == 0:
#             return num
        
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
                newProduct = AuctionItem.objects.create(
                    name=form.cleaned_data.get('name'),
                    active=True,
                    stripe_id=product.id,
                    description=form.cleaned_data.get('description'),
                    starting_bid=form.cleaned_data.get('starting_bid'),
                    current_bid=form.cleaned_data.get('starting_bid'),
                    value=form.cleaned_data.get('value'),
                    autobuy_price=form.cleaned_data.get('autobuy_price'),
                    auction=Auction.objects.get(id=auctionId),
                )
                for file in req.FILES.getlist('images'):
                    ItemImage.objects.create(file=file, item=newProduct)
                return redirect("auctionFront", 1)
            except:
                print('hi')
    return render(req, 'createProduct.html', {'form': form})

# ==={ Read Item }=== #

def displayItem(req: HttpRequest, auctionId:int, id: int) -> HttpResponse:
    item = AuctionItem.objects.get(id=id)
    images = [img for img in item.images.all()]

    if req.method == "POST":
        amount = req.POST.get('amount')
        stripe.api_key = settings.STRIPE_KEY  
        if amount != None and (int(amount) >= item.current_bid + 500):
            bid = Bid(bidder=Bidder.objects.get(id=req.POST.get("bidder")), amount=int(amount), item=AuctionItem.objects.get(id=req.POST.get("item")), setup_intent_id=req.POST.get("setup_intent"))
            print(bid)
            bid.save()
            item.current_bid = int(amount)
            item.save()
    lowestAllowedBid = item.current_bid + 500
    payment_method_id = req.POST.get("selected_payment_method")
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
    # form = CreateAuctionForm()
    if req.method == 'POST':
        form = CreateAuctionForm(req.POST)
        print(req.POST)
        if form.is_valid():
            try:
                print("testing")
                print(form.cleaned_data)
                # auction = Auction.objects.create(
                #     name=form.cleaned_data.get('name'),
                #     start_date=form.cleaned_data.get('start_date'),
                #     end_date=form.cleaned_data.get('end_date'),
                #     description=form.cleaned_data.get('description'),
                #     # active=True
                # )
                auction = form.save()

                print('hi')
                return redirect('auctionSettings', auction.id)
            except:
                print('Error Creating Auction')
    return redirect('auctionSettings')
    # return render(req, 'createAuction.html', {"form": form})

# ==={ Display Auction }=== #

def auctionFront(req: HttpRequest, id: int) -> HttpResponse:
    context = {'page': 'auction'}

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
        end_auction(req, id)
        for item in auction.auctionitem_set.all():
            item.active = False
            item.save()
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

# ==={ Delete Auction }=== #

def deleteAuction(req: HttpRequest, id: int) -> HttpResponse:

    try:
        auction = Auction.objects.get(id=id)
        auction.delete()
    except:
        print('Error')
    return redirect('auctionSettings')

# ==={ Update Auction }=== #

def viewAuctionsList(req: HttpRequest, id: int | None = None) -> HttpResponse:
    auctions = Auction.objects.all()
    if id == None:
        activeAuction = Auction.objects.first()
        if activeAuction != None:
            return redirect("auctionSettings", activeAuction.id)

    return render(req, 'auctionList.html', {'auctions': auctions, 'auctionId': id, "page": 'settings', 'auctionForm': CreateAuctionForm()})


# ==={ Auction Settings }=== #

def auctionSettings(req: HttpRequest, id: int) ->  HttpResponse:
    auctions = Auction.objects.all()
    auction = Auction.objects.get(id=id)

    return render(req, 'auctionSettings.html', {'auctions': auctions, 'auction': auction, 'auctionId': id, "page": 'settings', 'auctionForm': CreateAuctionForm()})


def auctionDashboard(req: HttpRequest, id: int) ->  HttpResponse:
    auctions = Auction.objects.all()
    auction = Auction.objects.get(id=id)

    return render(req, 'auctionDashboard.html', {'auctions': auctions, 'auction': auction, 'auctionId': id, "page": 'settings', 'auctionForm': CreateAuctionForm()})




# WORK IN PROGRESS #
def auctionHome(req: HttpRequest) -> HttpResponse:
    # if not req.user.is_authenticated or len(req.user.groups) == 0:
    #     activeAuction = Auction.objects.get(active=True)
    #     if activeAuction != None:
    #         return redirect("auctionFront", activeAuction.id)
    # else:
    for group in req.user.groups.all():
        if group.name == 'Admin':
            activeAuction = Auction.objects.first()
            if activeAuction != None:
                return redirect("auctionSettings", activeAuction.id)
    else:
        try:
            activeAuction = Auction.objects.get(active=True)
            return redirect("auctionFront", activeAuction.id)
        except:
            pass
        
    return render()



# ============{ USER AUTH VIEWS }============ #

# ==={ Register }=== #

def registration_view(request: HttpRequest):
    if request.method == "POST":
        form = Create_User_Form(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get("first_name")
            lastname = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            form.save()
            user = authenticate(request, username=User.objects.get(email=email).username, password=password)
            
            try:
                stripe.api_key = settings.STRIPE_KEY
                customer = stripe.Customer.create(
                    name=f"{firstname} {lastname}",
                    email=email,
                )
                bidder = Bidder.objects.create(
                    user=user,
                    stripe_id=customer.id,
                    bidder_id=user.username
                )
                

                if user.is_authenticated:
                    return redirect("login")
            except:
                print("Can't create customer")
    else:
        form = Create_User_Form()
    return render(request, "registration.html", {"form": form})


# ==={ User Settings }=== #

def account_settings(request: HttpRequest):
    return render(request, "account_settings.html")

def login_settings(request: HttpRequest):
    return render(request, "login_settings.html")

def update_name(request: HttpRequest):
    stripe.api_key = settings.STRIPE_KEY
    bidder = Bidder.objects.get(user=request.user)
    if request.method == "POST":
        form = UpdateNameForm(request.POST, instance=request.user)
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            form.save()
            stripe.Customer.modify(
                bidder.stripe_id,
                name= f"{first_name} {last_name}",
            )
            messages.success(request, "Your name was successfully updated!")
            return redirect("login_settings")
        else:
            messages.error(request, "Error")
    else:
        form = UpdateNameForm(instance=request.user)
    return render(request, "update_account.html", {"form": form})

def update_email(request: HttpRequest):
    stripe.api_key = settings.STRIPE_KEY
    bidder = Bidder.objects.get(user=request.user)
    if request.method == "POST":
        form = UpdateEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            form.save()
            stripe.Customer.modify(
                bidder.stripe_id,
                email=email,
            )
            messages.success(request, "Your email was successfully update!")
            return redirect("login_settings")
        else:
            messages.error(request, "Error")
    else:
        form = UpdateEmailForm(instance=request.user)
    return render(request, "update_account.html", {"form": form})

def update_password(request: HttpRequest):
    stripe.api_key = settings.STRIPE_KEY
    if request.method == "POST":
        form = UpdatePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("login_settings")
        else:
            messages.error(request, "Error")
    else:
        form = UpdatePasswordForm(request.user)
    return render(request, "update_account.html", {"form": form})

# ============{ MICHAELS VIEWS }============ #

def add_payment_method(request: HttpRequest):
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
        return redirect("payment_settings")
    return render(request, "edit_payment_method.html", {"card": payment_method, "month_list": month_list, "year_list": year_list})

def delete_payment_method(request: HttpRequest, payment_method_id):
    stripe.api_key = settings.STRIPE_KEY
    try:
        stripe.PaymentMethod.detach(payment_method_id)
    except:
        print("Can't remove payment method")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_setup_intent(request: HttpRequest, product_id, payment_method_id):
    stripe.api_key = settings.STRIPE_KEY
    bidder = Bidder.objects.get(user=request.user)
    customer = stripe.Customer.retrieve(id=bidder.stripe_id)

    setup_intent = stripe.SetupIntent.create(
        customer=customer.id,
        payment_method=payment_method_id,
        payment_method_types=['card'],
        metadata={
            "product_id": product_id,
        }
    )
    return setup_intent

def end_auction(request: HttpRequest, id):
    try:
        stripe.api_key = settings.STRIPE_KEY
        auction = Auction.objects.get(id=id)
        items = auction.auctionitem_set.all()

        bidders_invoices = {}

        for item in items:
            stripe_product = stripe.Product.retrieve(item.stripe_id)
            if item.active:
                stripe.Product.modify(
                    stripe_product.id,
                    active=False,
                )
            try:
                highest_bid = Bid.objects.filter(item=item).order_by("-amount").first()
                if highest_bid and highest_bid.setup_intent_id:
                    setup_intent = stripe.SetupIntent.retrieve(highest_bid.setup_intent_id)
                    if setup_intent and setup_intent.status == "succeeded":
                        stripe_customer = highest_bid.bidder.stripe_id
                        if stripe_customer not in bidders_invoices:
                            bidders_invoices[stripe_customer] = {
                                "items": [],
                                "payment_method": setup_intent.payment_method,
                            }
                        bidders_invoices[stripe_customer]["items"].append({
                            "amount": item.current_bid,
                            "name": item.name,
                        })
                        highest_bid.payment_intent_id = "PENDING"
                        highest_bid.save()
            except:
                print(f"Error {item.id}")
        
        for stripe_customer, invoice_data, in bidders_invoices.items():
            try:
                for invoice_item in invoice_data["items"]:
                    stripe_invoice_item = stripe.InvoiceItem.create(
                            customer=stripe_customer,
                            amount=invoice_item["amount"],
                            currency="usd",
                            description=invoice_item["name"],
                        )
                    logger.debug(f"Invoice Item: {stripe_invoice_item}")
                invoice = stripe.Invoice.create(
                    customer=stripe_customer,
                    default_payment_method=invoice_data["payment_method"],
                    auto_advance=True,
                )
                logger.debug(f"Invoice: {invoice}")
                finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)
                logger.debug(f"Finalized Invoice: {finalized_invoice}")
                Bid.objects.filter(bidder__stripe_id=stripe_customer, payment_intent_id="PENDING").update(payment_intent_id=finalized_invoice.id)
            except:
                print(f"Error creating invoice for bidder {stripe_customer}")
    except:
        print("Auction doesn't exist")
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