# myapp/forms.py
from django import forms
from django.core.exceptions import ValidationError

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit() or len(phone) != 11:
            raise ValidationError('Phone number must be a valid 11-digit number.')
        return phone

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) or not any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/`~' for char in password):
            raise ValidationError('Password must be at least 8 characters long and contain at least one uppercase letter, one digit, and one special character.')
        return password
