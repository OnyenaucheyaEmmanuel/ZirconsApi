# booking/views.py
from django.conf import settings
from django.contrib import messages
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Payment
from .paystack import Paystack
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        try:
            # Retrieve form data from the POST request
            serializer = PaymentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            team_name = serializer.validated_data['team_name']
            date = serializer.validated_data['date']
            players = serializer.validated_data['players']
            start_time = serializer.validated_data['start_time']

            # Ensure the number of players does not exceed 8
            if players > 8:
                messages.error(request, 'Number of players cannot exceed 8.')
                return Response({'error': 'Number of players cannot exceed 8.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the number of players for the given date and time
            existing_players = Payment.objects.filter(date=date, start_time=start_time, verified=True).values_list('players', flat=True)
            
            total_existing_players = sum(existing_players) if existing_players else 0
            if total_existing_players == 8:
                messages.error(request, 'The selected time slot for this date is already booked, and the team is complete.')
                return Response({'error': 'The selected time slot for this date is already booked, and the team is complete.'}, status=status.HTTP_400_BAD_REQUEST)
            elif total_existing_players + players > 8:
                remain_players = 8 - (total_existing_players)
                messages.info(request, f"You have exceeded the number of players to complete the team. We need {remain_players} players only")
                return Response({'info': f'You have exceeded the number of players to complete the team. We need {remain_players} players only'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                total_existing_players + players <= 8 
                remaining_players = 8 - (total_existing_players)
                messages.info(request, f'The selected time slot for this date has {remaining_players} spots remaining. Proceed to make payment.')

            # Calculate the amount based on the number of players
            amount = 500 * players

            # Create a new Payment instance
            payment = Payment.objects.create(
                amount=amount,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                team_name=team_name,
                date=date,
                start_time=start_time,
                players=players
            )

            context = {
                'payment': PaymentSerializer(payment).data,
                'paystack_pub_key': settings.PAYSTACK_PUBLIC_KEY,
                'amount_value': payment.amount_value(),
            }
            return Response(context)

        except Exception as e:
            messages.error(request, str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def verify_payment(self, request, pk=None):
        try:
            payment = self.get_object()
            verified = payment.verify_payment()

            if verified:
                # print(request.user.username, " Football Pitch Registration Successfully")
                return Response({'message': 'Football Pitch Registration Successfully'})
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
