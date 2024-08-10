from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.conf import settings
import stripe
from auction.models import *

# Create your views here.
def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'home.html')

def aboutUs(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')

def projectsPage(request: HttpRequest) -> HttpResponse:
    return render(request, 'projects.html')

def contactUs(request: HttpRequest) -> HttpResponse:
    return render(request, 'contactus.html')

def loginPage(request: HttpRequest) -> HttpResponse:
    return render(request, 'login.html')

def logoutUser(request: HttpRequest) -> HttpResponse:
    return render(request, 'logout.html')