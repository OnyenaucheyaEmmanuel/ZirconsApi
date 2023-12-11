# YourApp/urls.py
from django.urls import path
from .views import initiate_payment, verify_payment

urlpatterns = [
    path('initiate-payment/', initiate_payment, name='initiate_payment'),
    path('verify-payment/<str:ref>/', verify_payment, name='verify_payment'),
    # Add other URLs as needed
]
