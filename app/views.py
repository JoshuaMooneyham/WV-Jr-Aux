from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
# from django.conf import settings
# import stripe
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.decorators import *
from django.contrib.auth.models import User




# Create your views here.
def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'home.html')

def aboutUs(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')

def projectsPage(request: HttpRequest) -> HttpResponse:
    return render(request, 'projects.html')

def contactUs(request: HttpRequest) -> HttpResponse:
    return render(request, 'contactus.html')

# def loginPage(request: HttpRequest) -> HttpResponse:
#     return render(request, 'login.html')

# def logoutUser(request: HttpRequest) -> HttpResponse:
#     return render(request, 'logout.html')

def scholarShip(request:HttpRequest) -> HttpResponse:
    return render(request, 'scholarship.html')

def supportUs(request: HttpRequest) -> HttpResponse:
    return render(request, 'support.html')


@unauthenticated_user
def login_view(req: HttpRequest) -> HttpResponse:
    print('HI')
    if req.user.is_authenticated:
        print("Testing1")
        return redirect('auction')

    if req.method == 'POST':
        email = req.POST.get('email')
        password = req.POST.get('password')
        
        user = authenticate(req, username=User.objects.get(email=email).username, password=password)

        if user is not None:
            login(req, user)
            return redirect('auctionFront', 20)
        else:
            messages.info(req, 'Username or Password incorrect')

    return render(req, 'login.html')

@login_required(login_url="login")
def logout_view(request: HttpRequest):
    logout(request)
    return redirect("login")


