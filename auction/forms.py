from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from auction.models import *
from django.core.exceptions import ValidationError
import random


def random_username(sender, instance, **kwargs):
    if not instance.username:
        instance.username = random.randint(100000000, 999999999)

models.signals.pre_save.connect(random_username, sender=User)

class Create_User_Form(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(f"The email {email} is already in use.")
        else:
            return email
        
class UpdateNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]

class UpdatePasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["old_password", "new_password1", "new_password2"]

class CreateAuctionItemForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ['name', 'description', 'starting_bid', 'autobuy_price', 'value']

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)

# class PlaceBidForm(forms.ModelForm):
#     class Meta:
#         model = Bid
#         fields = ['bidder', 'amount', 'item']

class CreateAuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['name', 'start_date', 'end_date', "active"]