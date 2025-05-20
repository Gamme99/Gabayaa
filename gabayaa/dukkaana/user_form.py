from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from .user_model import Customer
from .models import Customer


class CustomerForm(UserCreationForm):
    username = forms.CharField(
        error_messages={
            'required': 'username is required',
            'unique': 'username is taken.',
            'invalid': 'Enter a valid username.'
        }
    )
    first_name = forms.CharField(
        error_messages={'required': 'first name is required.'}
    )
    last_name = forms.CharField(
        error_messages={'required': 'last name is required.'}
    )
    email = forms.EmailField(
        error_messages={
            'required': 'username is required',
            'unique': ' Account with this email already exists.',
            'invalid': 'Enter a valid email.'
        }
    )
    phone_number = forms.CharField(
        error_messages={'required': 'phone is required'}
    )
    street_address = forms.CharField(
        error_messages={'required': 'street address is required'}
    )
    city = forms.CharField(
        error_messages={'required': 'city is required'}
    )
    state = forms.CharField(
        error_messages={'required': 'state is required'}
    )
    zip_code = forms.CharField(
        error_messages={'required': 'zip code is required.'}
    )
    # billing_address = forms.CharField(
    #     error_messages={'required': 'billing address is required.'}
    # )
    password1 = forms.CharField(
        help_text='Must be at least 8 characters long.',
        error_messages={'required': 'password is required.'}
    )
    password2 = forms.CharField(
        error_messages={'required': 'Please confirm your password.'}
    )

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
