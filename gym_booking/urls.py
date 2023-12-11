# gym/urls.py
from django.urls import path, include
from rest_framework import routers
from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationAPIView, UserLoginAPIView

router = routers.DefaultRouter()
router.register(r'gym-memberships', GymMembershipViewSet)
router.register(r'payments', PaymentViewSet)




urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('gym-payment/', gym_payment_api, name='gym-payment-api'),
    path('verify-gym/<str:ref>/', verify_gym_api, name='verify-gym-api'),
    path('gymdashboard/', GymDashboardAPI.as_view(), name='gymdashboard-api'),

]
