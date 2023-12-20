# myapp/serializers.py
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# gym_booking/serializers.py
from rest_framework import serializers

from .models import GymMembership, Payment


class GymMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymMembership
        fields = '__all__'
from rest_framework import serializers

from .models import CustomUser
from .utils import generate_user_id  # Import the function


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Override create to handle the custom 'user_id' field
        user_id = generate_user_id()
        user = CustomUser.objects.create_user(user_id=user_id, **validated_data)
        return user


    def validate_password(self, password):
        # Password must be at least 8 characters long
        if len(password) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')

        # Password must contain at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError('Password must contain at least one uppercase letter.')

        # Password must contain at least one digit
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError('Password must contain at least one digit.')

        # Password must contain at least one special character
        special_characters = '!@#$%^&*()-_=+[]{}|;:,.<>?/`~'
        if not any(char in special_characters for char in password):
            raise serializers.ValidationError('Password must contain at least one special character.')

        return password


class UserLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(required=True, write_only=True)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit() or len(phone) != 11:
            raise ValidationError('Phone number must be a valid 11-digit number.')
        return phone
        
    def validate(self, data):
        username_or_email = data.get("username_or_email")
        password = data.get("password")

        if username_or_email and password:
            # Try to authenticate with username
            user = authenticate(username=username_or_email, password=password)

            if not user:
                # If not successful, try to authenticate with email
                try:
                    user = User.objects.get(email=username_or_email)
                    user = authenticate(username=user.username, password=password)
                except User.DoesNotExist:
                    pass

            if user:
                data["user"] = user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username_or_email' and 'password'.")

        return data





class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        ref_name = 'gym_booking_payment'
