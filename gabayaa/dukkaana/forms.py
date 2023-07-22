from django.contrib import admin
from .models import Product, Shoe, Cloth, Electronic
from django.forms import ModelForm
from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class ClothForm(ModelForm):
    class Meta(ProductForm.Meta):
        model = Cloth


class ShoeForm(ModelForm):
    class Meta(ProductForm.Meta):
        model = Shoe


class ElectronicForm(ModelForm):
    class Meta(ProductForm.Meta):
        model = Electronic
