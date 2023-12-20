# football_pitch/serializers.py
from rest_framework import serializers

from football_pitch.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        ref_name = 'football_pitch_payment'
