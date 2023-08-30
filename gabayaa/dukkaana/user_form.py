from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from .user_model import Customer
from .models import Customer


class CustomerForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number',
                  'street_address', 'city', 'state', 'zip_code', 'billing_address', 'password1', 'password2']


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number',
                  'street_address', 'city', 'state', 'zip_code', 'billing_address']


class LoginForm(AuthenticationForm):
    pass
