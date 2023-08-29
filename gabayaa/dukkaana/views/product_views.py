from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest

# from ..models import Cloth, Shoe, Electronic, ProductImage, Product
from ..models import ProductImage, Product


def cloths(request):
    products = Product.objects.filter(category="Cloth")
    return render(request, 'view/products.html', {'products': products})


def shoes(request):
    products = Product.objects.filter(category="Shoe")
    return render(request, 'view/products.html', {'products': products})


def electronics(request):
    products = Product.objects.filter(category="Electronic")
    return render(request, 'view/products.html', {'products': products})


def renting(request):
    return render(request, 'renting.html', {})


def buying(request):
    return render(request, 'buying.html', {})


def product_info(request, category, id):

    print("------------d in here: ", id)
    product = None

    product = Product.objects.get(id=id)

    if product:
        # Retrieve all ProductImage instances associated with the product
        product_images = ProductImage.objects.filter(productId=id)
        return render(request, 'view/product_info.html', {'product': product, 'product_images': product_images})
    else:
        return HttpResponse('Product not found')
