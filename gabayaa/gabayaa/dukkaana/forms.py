from django.contrib import admin
# from .models import Product, Shoe, Cloth, Electronic, ProductImage
from .models import Product, ProductImage, PromoCode, Review
from django.forms import ModelForm
from django import forms


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
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
