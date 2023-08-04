from django.contrib import admin
from .models import Product, Shoe, Cloth, Electronic, ProductImage
from django.forms import ModelForm
from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        exclude = ['images']


class ClothForm(forms.ModelForm):
    class Meta(ProductForm.Meta):
        model = Cloth
        exclude = ['image']


class ShoeForm(forms.ModelForm):
    class Meta(ProductForm.Meta):
        model = Shoe
        fields = ['category', 'type', 'size', 'name', 'price',
                  'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize the error messages for specific fields
        self.fields['category'].error_messages = {
            'required': '*',
            # 'required': 'Please select a category for the shoe.',
        }

        self.fields['type'].error_messages = {
            'required': '*',
            # 'required': 'Please select a type for the shoe.',
        }

        self.fields['size'].error_messages = {
            # 'required': 'Please select a size for the shoe.',
            'required': '*',
        }

        self.fields['name'].error_messages = {
            'required': '*',
        }

        self.fields['price'].error_messages = {
            'required': '*',
        }

        self.fields['description'].error_messages = {
            'required': '*',
        }


class ElectronicForm(forms.ModelForm):
    class Meta(ProductForm.Meta):
        model = Electronic
        exclude = ['image']
