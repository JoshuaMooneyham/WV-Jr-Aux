"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from app.views import *
from auction.views import *

urlpatterns = [
    path('testing/', testingView, name='testing'),
    path('registration/', registration_view, name='registration'),
    path('add-payment-method/', add_payment_view, name='add_payment_method'),
    path('create-payment-intent/<str:product_id>', create_payment_intent, name='create_payment_intent'),
    path('end-auction/<str:payment_intent_id>', end_auction, name='end_auction'),
    path('products/create', productsTest, name='createProduct'),
    path('', auctionFront, name="auctionFront"),
    path('products/<int:id>', displayItem, name='displayProduct'),
    path('create/', createAuction, name='createAuction'),
    path('<int:id>/', auctionFront, name="auctionFront"),
    path('products/<int:id>/', displayItem, name='displayProduct'),
    path('products/create/', productsTest, name='createProduct'),
    path('products/delete/<int:id>/', deleteItem, name="deleteItem"),
    path('products/place_bid/<str:product_id>/', create_payment_intent, name='create_payment_intent'),
]