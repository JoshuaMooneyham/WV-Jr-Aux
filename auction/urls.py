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
from django.conf.urls.static import static
from app.views import *
from auction.views import *

urlpatterns = [

    path("", auctionHome, name="auction"),

    # ==={ Item CRUD }=== #
    path('<int:auctionId>/products/create/', createProduct, name='createProduct'),
    path('<int:auctionId>/products/<int:id>/', displayItem, name='displayProduct'),
    path('<int:auctionId>/products/update/<int:id>/', updateItem, name='updateProduct'),
    path('<int:auctionId>/products/delete/<int:id>/', deleteItem, name="deleteProduct"),

    # ==={ Auction CRUD }=== #
    path('create/', createAuction, name='createAuction'),
    path('<int:id>/', auctionFront, name="auctionFront"),
    path('<int:id>/delete/', deleteAuction, name='deleteAuction'),
    path('<int:id>/config/', auctionSettings, name="auctionSettings"),
    path('<int:id>/dashboard/', auctionDashboard, name="auctionDashboard"),
    # path('config/', viewAuctionsList, name="auctionSettings"),
    # ^^^ NOT DUPLICATES dont delete

    # ==={ User Auth }=== #
    path('registration/', registration_view, name='registration'),
    path('account-settings/', account_settings, name='account_settings'),
    path('login-settings/', login_settings, name='login_settings'),
    path('update-name/', update_name, name='update_name'),
    path('update-email/', update_email, name='update_email'),
    path('update-password/', update_password, name='update_password'),
    
    # ==={ Michaels URLs im not really sure }=== #
    path('add-payment-method/', add_payment_method, name='add_payment_method'),
    path('edit-payment-method/<str:payment_method_id>/', edit_payment_method, name='edit_payment_method'),
    path('delete-payment-method/<str:payment_method_id>/', delete_payment_method, name="delete_payment_method"),
    path('payment-method-settings/', payment_settings, name='payment_settings'),
    path('end-auction/<int:id>/', end_auction, name='end_auction'),
    path('get-invoices/<int:id>/', get_invoices_for_auction, name='get_invoices'),

    # ==={ PDF Files }=== #
    path('view-pdf/<str:invoice_id>/', view_invoice_pdf, name='view_pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)