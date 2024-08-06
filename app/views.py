from django.shortcuts import render
import stripe

# Create your views here.
stripe.api_key = "sk_test_51PjAGPHJI2ETfc7Unl87pI7nlHuY661QU3SQh4fxpHeh8pilFfX4izyqv8x7i9KlTu2XyXvaw1AXMmyYXIC3mmHr00gTogEk1w"
customers = stripe.Customer.list()
customer = stripe.Customer.retrieve("cus_Qayy8h85WAtWRo")
customer.delete()
print(customers)