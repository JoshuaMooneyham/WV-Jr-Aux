from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib import messages
import stripe.error
from django.utils.timezone import make_aware
from auction.models import *
from auction.forms import *
from django.conf import settings
from django.core.files.base import ContentFile
from typing import Dict, List
import stripe, json, logging, os, requests
from django.urls import reverse

logger = logging.getLogger(__name__)

import random
import datetime
import zoneinfo
import re


def generateBidderId() -> int:
    while True:
        num: int = random.randint(100000000, 999999999)
        if len(Bidder.objects.filter(bidder_id=num)) == 0:
            return num
# TOPP
def dateTimeConversion(date: datetime.datetime) -> datetime.datetime:          
    return datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond, zoneinfo.ZoneInfo('America/Chicago'))

def stringifyDate(date: datetime.datetime) -> str:
    months = ['', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
    return f'{months[date.month]} {date.day}, {date.year} at {date.hour if date.hour < 13 and date.hour > 0 else "12" if date.hour == 0 else date.hour - 12}:{date.minute if date.minute > 9 else "0"+str(date.minute)} {"AM" if date.hour < 12 else "PM"}'

# def generateBidderId() -> int:
#     while True:
#         num: int = random.randint(100000000, 999999999)
#         if len(Bidder.objects.filter(bidder_id=num)) == 0:
#             return num
        
# Create your views here.

# ============{ ITEM VIEWS }============ #

# ==={ Create Item }=== #

def createProduct(req: HttpRequest, auctionId: int) -> HttpResponse:
    auction = Auction.objects.get(id=auctionId)
    
    form = CreateAuctionItemForm()
    if req.method == 'POST':
        form = CreateAuctionItemForm(req.POST)
        # print(req.POST)
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
                return redirect("auctionFront", auctionId)
            except:
                print('hi')
    return render(req, 'createProduct.html', {'form': form, 'auction': auction, 'auctionId': auctionId})

# ==={ Read Item }=== #

def displayItem(req: HttpRequest, auctionId:int, id: int) -> HttpResponse:
    item = AuctionItem.objects.get(id=id)
    images = [img for img in item.images.all()]

    auctions = Auction.objects.all()
    auction = Auction.objects.get(id=auctionId)

    if req.method == "POST":
        amount = req.POST.get('amount')
        stripe.api_key = settings.STRIPE_KEY
        if amount != None and (int(amount) >= item.current_bid + 500):
            bidder = Bidder.objects.get(id=req.POST.get("bidder"))
            payment_methods = list_payment_methods(req)
            if len(payment_methods) != 0:
                bid = Bid(bidder=bidder, amount=int(amount), item=AuctionItem.objects.get(id=req.POST.get("item")), setup_intent_id=req.POST.get("setup_intent"))
                bid.save()
                item.current_bid = int(amount)
                item.highest_bidder = bidder
                item.save()
            else:
                req.session['return_url'] = req.build_absolute_uri()
                return redirect("add_payment_method")
    lowestAllowedBid = (item.current_bid + 500) if item.highest_bidder is not None else item.current_bid
    payment_method_id = req.POST.get("selected_payment_method")
    if req.user.is_authenticated:
        setup_intent = create_setup_intent(req, item.stripe_id, payment_method_id)
        saved_cards = list_payment_methods(req)
    else:
        setup_intent = None
        saved_cards = None

            
    return render(req, 'displayItem.html', {'auctions': auctions, 'auction': auction, "item": item, "images": images, "lab": lowestAllowedBid, "setup_intent": setup_intent, "saved_cards": saved_cards, "STRIPE_TEST_PUBLIC_KEY": settings.STRIPE_TEST_PUBLIC_KEY, "auctionId": auctionId})

# ==={ Update Item }=== #

def updateItem(req: HttpRequest, auctionId: int, id: int) -> HttpResponse:

    auction = Auction.objects.get(id=auctionId)
    item = AuctionItem.objects.get(id=id)

    return render(req, 'updateItem.html', {'auction': auction, 'item': item, 'auctionId': auctionId})

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
    context = {'page': 'auction', 'auctionId': id}

    auction = Auction.objects.get(id=id)
    context['auction'] = auction
    context["items"] = auction.auctionitem_set.all()
    startTime = dateTimeConversion(auction.start_date)
    endTime = dateTimeConversion(auction.end_date)
    now = make_aware(datetime.datetime.now())
    if now > endTime:
        context["over"] = True
        if auction.active:
            end_auction(req, id)
            for item in auction.auctionitem_set.all():
                item.active = False
                item.save()
            auction.active = False
            
    elif now > startTime:
        left = endTime - now
        hours, remainder = divmod(left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        hours += left.days * 86400 / 3600
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
    form = CreateAuctionForm()
    auctions = Auction.objects.all()
    auction = Auction.objects.get(id=id)

    start = dateTimeConversion(auction.start_date)
    startDate:str = f'{start.date()}'
    startTime:str = f'{start.time()}'
    startDateTime:str= f'{startDate}T{startTime}Z'
    stringStart:str = stringifyDate(start)


    end = dateTimeConversion(auction.end_date)
    endDate:str = f'{end.date()}'
    endTime:str = f'{end.time()}'
    endDateTime:str = f'{endDate}T{endTime}Z'
    stringEnd:str = stringifyDate(end)

    now = dateTimeConversion(datetime.datetime.now())

    startable = now < start
    endable = now > start and now < end
    
    if req.method == 'POST':
        form = CreateAuctionForm(req.POST)
        if form.is_valid():
            try:
                auction.name = form.cleaned_data.get('name')
                auction.start_date = form.cleaned_data.get('start_date')
                auction.end_date = form.cleaned_data.get('end_date')
                auction.save()
            except:
                print('Error updating auction')

    return render(req, 'auctionSettings.html', {'startable': startable, 'endable': endable, 'stringEnd': stringEnd, 'endDateTime': endDateTime, 'endTime': endTime, 'endDate': endDate, 'stringStart': stringStart, 'startDateTime': startDateTime, 'startTime': startTime, 'startDate': startDate, 'auctions': auctions, 'auction': auction, 'auctionId': id, "page": 'settings', 'auctionForm': form})


def auctionDashboard(req: HttpRequest, id: int) ->  HttpResponse:
    auctions = Auction.objects.all()
    auction = Auction.objects.get(id=id)

    items = auction.auctionitem_set.all()
    bids = 0
    total = 0
    unbid_items = 0
    for item in items:
        bid = item.bid_set.all().count()
        bids += bid
        if item.highest_bidder is not None:
            total += item.current_bid
        if bid == 0:
            unbid_items += 1

    itemsWBids = len(items) - unbid_items
    fees = (total * .029) + (30 * itemsWBids)
    profit = total - fees
    # months = ['', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
    end = dateTimeConversion(auction.end_date)
    start = dateTimeConversion(auction.start_date)
    # stringStart = f'{months[start.month]} {start.day}, {start.year} at {start.hour if start.hour < 13 and start.hour > 0 else "12" if start.hour == 0 else start.hour - 12}:{start.minute if start.minute > 9 else "0"+str(start.minute)} {"AM" if start.hour < 12 else "PM"}'
    # stringEnd = f'{months[end.month]} {end.day}, {end.year} at {end.hour if end.hour < 13 and end.hour > 0 else "12" if end.hour == 0 else end.hour - 12}:{end.minute if end.minute > 9 else "0"+str(end.minute)} {"AM" if end.hour < 12 else "PM"}'
    stringStart = stringifyDate(start)
    stringEnd = stringifyDate(end)

    return render(req, 'auctionDashboard.html', {'auctions': auctions, 'profit': f'{profit / 100:,.2f}', 'start': stringStart, 'end': stringEnd, 'fees': f'{fees / 100:,.2f}', 'bidOnItems': itemsWBids, 'total':total, 'bids': bids, 'items': items, 'auction': auction, 'auctionId': id, "page": 'settings', 'auctionForm': CreateAuctionForm()})




# WORK IN PROGRESS #
def auctionHome(req: HttpRequest) -> HttpResponse:
    if not req.user.is_authenticated or len(req.user.groups.all()) == 0:
        activeAuction = Auction.objects.get(active=True)
        if activeAuction != None:
            return redirect("auctionFront", activeAuction.id)
    else:
        for group in req.user.groups.all():
            if group.name == 'Admin':
                activeAuction = Auction.objects.first()
                if activeAuction != None:
                    return redirect("auctionSettings", activeAuction.id)
    # else:
    #     try:
    #         activeAuction = Auction.objects.get(active=True)
    #         return redirect("auctionFront", activeAuction.id)
    #     except:
    #         pass
        
    # return render()



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
    try:
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
    except:
        print("Can't update name")
    return render(request, "update_account.html", {"form": form})

def update_email(request: HttpRequest):
    try:
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
    except:
        print("Can't update email")
    return render(request, "update_account.html", {"form": form})

def update_password(request: HttpRequest):
    try:
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
    except:
        print("Can't update password")
    return render(request, "update_account.html", {"form": form})

# ============{ MICHAELS VIEWS }============ #

def add_payment_method(request: HttpRequest):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')

            if not payment_method_id:
                return JsonResponse({'error': 'Payment Method ID is required'}, status=400)

            stripe.api_key = settings.STRIPE_KEY
            bidder = Bidder.objects.get(user=request.user)

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

            # Prepare success response with redirect URL if available
            return_url = request.session.get('return_url')
            if return_url:
                del request.session['return_url']
                return JsonResponse({'redirect_url': return_url})
            else:
                return JsonResponse({'redirect_url': reverse("payment_settings")})
        
        except stripe.error.CardError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except stripe.error.InvalidRequestError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except stripe.error.AuthenticationError as e:
            return JsonResponse({'error': str(e)}, status=401)
        except stripe.error.APIConnectionError as e:
            return JsonResponse({'error': str(e)}, status=502)
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=500)
        except Bidder.DoesNotExist:
            return JsonResponse({'error': 'Bidder not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred: ' + str(e)}, status=500)

    return render(request, "add_payment.html", {'STRIPE_TEST_PUBLIC_KEY': settings.STRIPE_TEST_PUBLIC_KEY})

def list_payment_methods(request: HttpRequest):
    try:
        bidder = Bidder.objects.get(user=request.user)
        payment_methods = stripe.PaymentMethod.list(
            customer=bidder.stripe_id,
            type="card",
        )
    except:
        print("Can't list payments")
    return payment_methods

def payment_settings(request: HttpRequest):
    try:
        stripe.api_key = settings.STRIPE_KEY
        saved_cards = list_payment_methods(request)
    except:
        print("Can't get payment methods")
    return render(request, "payment_settings.html", {"saved_cards": saved_cards})

def edit_payment_method(request: HttpRequest, payment_method_id):
    try:
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
    except:
        print("Can't edit payment method.")
    return render(request, "edit_payment_method.html", {"card": payment_method, "month_list": month_list, "year_list": year_list})

def delete_payment_method(request: HttpRequest, payment_method_id):
    try:
        stripe.api_key = settings.STRIPE_KEY
        stripe.PaymentMethod.detach(payment_method_id)
    except:
        print("Can't remove payment method")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_setup_intent(request: HttpRequest, product_id, payment_method_id):
    try:
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
    except:
        print("Error creating setup intent.")
    return setup_intent

def end_auction(request: HttpRequest, id):
    try:
        stripe.api_key = settings.STRIPE_KEY
        auction = Auction.objects.get(id=id)
        items = auction.auctionitem_set.all()

        InvoiceItem = Dict[str, int]
        bidders_invoices: Dict[str, Dict[str, List[InvoiceItem]]] = {}  # type: ignore

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
                            "name": item.name,
                            "amount": item.current_bid,
                        })
                        highest_bid.payment_intent_id = "PENDING"
                        highest_bid.save()
            except Exception as e:
                print(f"Error with item {item.id}: {e}")

        for stripe_customer, invoice_data in bidders_invoices.items():
            try:
                for invoice_item in invoice_data["items"]:
                    stripe.InvoiceItem.create(
                        customer=stripe_customer,
                        amount=invoice_item["amount"],
                        currency="usd",
                        description=invoice_item["name"],
                    )
                    
                invoice = stripe.Invoice.create(
                    customer=stripe_customer,
                    default_payment_method=invoice_data["payment_method"],
                    auto_advance=True,
                    pending_invoice_items_behavior="include",
                )
                
                # Wait for invoice to be finalized
                finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)
                
                # Retrieve and log invoice lines
                invoice_lines = stripe.Invoice.list_lines(invoice.id)
                
                Bid.objects.filter(bidder__stripe_id=stripe_customer, payment_intent_id="PENDING").update(payment_intent_id=finalized_invoice.id)
            except Exception as e:
                print(f"Error creating invoice for bidder {stripe_customer}: {e}")

    except Exception as e:
        print(f"Error with auction {id}: {e}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def get_invoices_for_auction(request:HttpRequest, id:int) -> HttpResponse:
    try:
        stripe.api_key = settings.STRIPE_KEY
        bidders_invoices = {}
        auction = Auction.objects.get(id=id)
        items = auction.auctionitem_set.all()
        for item in items:
            if item.highest_bidder:
                bidder_id = item.highest_bidder.bidder_id
                bidder = Bidder.objects.get(bidder_id=bidder_id)
                bids = Bid.objects.filter(item=item, bidder=bidder)
                for bid in bids:
                    invoice_id = bid.payment_intent_id
                    if invoice_id:
                        invoice = stripe.Invoice.retrieve(invoice_id)

                        # pdf_url = invoice.invoice_pdf
                        # pdf_response = requests.get(pdf_url)
                        # pdf_file = ContentFile(pdf_response.content, f"{invoice_id}.pdf")
                        # pdf_path = os.path.join(settings.MEDIA_ROOT, f"{invoice_id}.pdf")

                        # with open(pdf_path, "wb") as f:
                        #     f.write(pdf_response.content)

                        if bidder_id not in bidders_invoices:
                            bidders_invoices[bidder_id] = {
                                "bidder_name": invoice.customer_name,
                                "amount_due": "{:.2f}".format(invoice.amount_due/100),
                                "status": invoice.status.upper(),
                                "invoice_id": invoice_id,
                                }
        logger.debug(f"bidders_invoices: {bidders_invoices}")
    except:
        print("Auction not found.")
        auction = None
    return render(request, "invoices.html", {'auction':auction , 'auctionId': id, "invoices": bidders_invoices})

def view_invoice_pdf(request: HttpRequest, invoice_id):
    try:
        stripe.api_key = settings.STRIPE_KEY
        invoice = stripe.Invoice.retrieve(invoice_id)
        pdf_url = invoice.invoice_pdf
        pdf_response = requests.get(pdf_url)
        pdf_content = pdf_response.content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{invoice_id}.pdf"'
        return response
    except Exception as e:
        print(f"Error retrieving PDF: {e}")
        return HttpResponse("Error retrieving PDF.")

def testingView(req: HttpRequest) -> HttpResponse:
    try:
        stripe.api_key = settings.STRIPE_KEY
        customers = stripe.Customer.list()
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