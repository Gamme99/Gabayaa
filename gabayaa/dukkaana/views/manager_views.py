from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
# from ..models import Cloth, Shoe, Electronic, ProductImage
# from ..forms import ProductForm, ShoeForm, ClothForm, ElectronicForm
from ..models import ProductImage, Product
from ..forms import ProductForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required(login_url="login")
def view_products(request):
    cloth_products = Product.objects.filter(category='Cloth')
    shoe_products = Product.objects.filter(category='Shoe')
    electronic_products = Product.objects.filter(category='Electronic')
    print(electronic_products)

    context = {
        'cloth_products': cloth_products,
        'shoe_products': shoe_products,
        'electronic_products': electronic_products,
    }

    return render(request, 'manager/view_products.html', context)


def search_products(request):
    query = request.GET.get('q')  # Get the search query from the request

    if query:
        # Perform a search based on the query across all three models
        product = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

        # Combine the results from all three models
        results = list(product)
    else:
        # If no query is provided, return all products
        results = []

    context = {
        'results': results,
        'query': query
    }

    return render(request, 'search_results.html', context)


# saves images and connect to right item through its primary key
def handle_product_images(product, images, request):

    print("product is:", product)

    first_image = None

    for image in images:
        # Create a ProductImage object, associate it with the product, and save it
        product_image = ProductImage.objects.create(
            image=image,
            productId=product
        )
        product_image.save()

        # Set the first saved image if it's not set yet
        if not first_image:
            first_image = product_image.image

    return first_image


@login_required(login_url="login")
def add_product(request):
    message = ""
    category = request.POST.get('category')
    print("category: ", category)
    if request.method == 'POST':

        form = ProductForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")

        # return redirect("manager")
        if form.is_valid():
            # Save the product information
            product = form.save()

            first_image = handle_product_images(product, images, request)
            if first_image:
                print("first image: ", first_image)
                product.image = first_image
            product.save()

            # Handle successful product creation
            message = "success"
            messages.success(request, 'successfully added new product')
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            # return redirect('add_product')
        else:
            if 'submit' in request.POST:
                print("wont submit form: ")
                messages.error(
                    request, 'failed to add new product. try again!')

    else:
        return redirect("manager")

    context = {'form': form, 'message': message, 'category': category}
    return render(request, 'forms/add_product.html', context)


def edit_product(request, id):
    # Step 1: Retrieve the specific product
    product = get_object_or_404(Product, id=id)
    form = ProductForm(request.POST or None, instance=product)
    images = request.FILES.getlist("images")

    # print(product.description)
    print(form)
    if request.method == 'POST':
        if 'save_changes' in request.POST:
            if form.is_valid():
                print("valid so saved")

                first_image = handle_product_images(product, images, request)
                if first_image:
                    product.image = first_image
                product.save()
                messages.success(request, 'successfully update the product')

    return render(request, 'forms/edit_product.html', {'form': form})


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'successfully deleted the product')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # Redirect to the search page in case of a GET request
    return redirect("search_product")
