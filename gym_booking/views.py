from .utils import generate_user_id  # Import the function

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import GymMembership, Payment
from .serializers import GymMembershipSerializer, PaymentSerializer
from .paystack import Paystack
from rest_framework import permissions
from django.shortcuts import get_object_or_404
# gym_booking/views.py
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from .serializers import UserLoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import GymMembership, Payment
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import GymMembership, Payment
from .serializers import PaymentSerializer  # Create this serializer if not already done
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import GymMembership, Payment
from django.shortcuts import render, redirect
from django.contrib import messages

# views.py

from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer

# views.py

from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import GymMembership
from .serializers import UserRegistrationSerializer, GymMembershipSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from .utils import generate_user_id  # Import the function

from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from .models import CustomUser
class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Override the user_id with a 4-digit value
        serializer.validated_data['user_id'] = generate_user_id()

        # Call the create method on the serializer
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'detail': 'User registered successfully.'}, status=status.HTTP_201_CREATED, headers=headers)

class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Print or log debugging information
        print(f"Login attempt with data: {request.data}")

        user = serializer.validated_data["user"]
        login(request, user)
        return Response({'detail': 'User logged in successfully.'}, status=status.HTTP_200_OK)

class GymMembershipViewSet(viewsets.ModelViewSet):
    queryset = GymMembership.objects.all()
    serializer_class = GymMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def current_user_membership(self, request):
        user_membership = get_object_or_404(GymMembership, user=request.user)
        serializer = self.get_serializer(user_membership)
        return Response(serializer.data)

    # Add other actions and overrides as needed

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def verify(self, request, pk):
        payment = self.get_object()
        paystack = Paystack()
        status, result = paystack.verify_payment(payment.ref, payment.amount)

        if status:
            # Process the payment verification result...
            return Response({'detail': 'Payment verified successfully'}, status=status.HTTP_200_OK)
        else:
            # Handle verification failure...
            return Response({'detail': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)

    # Add other actions and overrides as needed



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gym_payment_api(request):
    try:
        # Get or create GymMembership for the user
        user_wallet, created = GymMembership.objects.get_or_create(user=request.user)

        # Check if the plan is still active
        if user_wallet.plan_status:
            error_message = f"{user_wallet.plan} Plan is still active. You cannot make another payment."
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve payment details from the request data
        amount = request.data.get('amount')
        email = request.user.email

        # Create a new Payment instance
        payment = Payment.objects.create(amount=amount, email=email, user=request.user)
        payment.save()

        serializer = PaymentSerializer(payment)

        context = {
            'payment': serializer.data,
            'field_values': request.data,
            'paystack_pub_key': settings.PAYSTACK_PUBLIC_KEY,
            'amount_value': payment.amount_value(),
        }
        return Response(context, status=status.HTTP_201_CREATED)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_gym_api(request, ref):
    try:
        payment = Payment.objects.get(ref=ref)
        verified = payment.verify_payment()

        user_wallet = GymMembership.objects.get(user=request.user)

        if verified:
            if payment.amount == 500:
                user_wallet.plan = "Bronze"
                user_wallet.set_expiration_date(14)
            elif payment.amount == 1000:
                user_wallet.plan = "Silver"
                user_wallet.set_expiration_date(30)
            elif payment.amount == 1500:
                user_wallet.plan = "Gold"
                user_wallet.set_expiration_date(60)

            user_wallet.save()
            print(request.user.username, " Membership registration successfully")
            return Response({'message': 'Membership registration successful'}, status=status.HTTP_200_OK)

        return Response({'message': 'Verification failed'}, status=status.HTTP_400_BAD_REQUEST)

    except Payment.DoesNotExist:
        return Response({'message': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    except GymMembership.DoesNotExist:
        return Response({'message': 'Gym membership not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GymDashboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Retrieve the user's gym membership
            user_membership = GymMembership.objects.get(user=request.user)
            user_membership.set_plan_status()
            payment_history = Payment.objects.filter(user=request.user)

            context = {
                'user_membership': {
                    'user_id': request.user.user_id,
                    'plan': user_membership.plan,
                    'plan_status': user_membership.plan_status,
                },
                'payment_history': [
                    {
                        'amount': payment.amount,
                        'verified': payment.verified,
                        'ref': payment.ref,
                        'date_created': payment.date_created,
                    }
                    for payment in payment_history
                ],
            }

            return Response(context)

        except GymMembership.DoesNotExist:
            return Response({'error_message': 'Gym membership not found.'}, status=404)

