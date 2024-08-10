from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from auction.models import *

class Create_User_Form(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

class CreateAuctionItemForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ['name', 'description', 'starting_bid', 'autobuy_price']

# class CreateItemImageForm(forms.ModelForm):
#     class Meta:
#         model = ItemImage
#         fields = ['file']