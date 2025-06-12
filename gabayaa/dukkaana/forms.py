from django.contrib import admin
# from .models import Product, Shoe, Cloth, Electronic, ProductImage
from .models import Product, ProductImage, PromoCode, Review
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # fields = '__all__'
        fields = ["category", "name", "price", "description"]


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        exclude = ['images']


class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = '__all__'


class ReviewForm(forms.ModelForm):
    """
    Form for adding and editing product reviews.
    """
    class Meta:
        model = Review
        fields = ['title', 'rating', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': _('Give your review a title')
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'min': '1',
                'max': '5',
                'step': '1',
                'placeholder': _('Rate from 1 to 5')
            }),
            'comment': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'rows': '4',
                'placeholder': _('Write your review here...')
            })
        }


class CheckoutForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'})
    )
    full_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'})
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full', 'rows': 3})
    )
    city = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'})
    )
    state = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'})
    )
    zip_code = forms.CharField(
        required=True,
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'})
    )
    phone = forms.CharField(
        required=True,
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'})
    )
