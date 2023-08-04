from django.shortcuts import render, redirect

from ..models import Cloth, Shoe, Electronic, ProductImage
from ..forms import ProductForm, ShoeForm, ClothForm, ElectronicForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required(login_url="login")
def view_products(request):

    context = {}
    return render(request, 'manager/view_products.html', context)


def search_products(request):
    query = request.GET.get('q')  # Get the search query from the request

    if query:
        # Perform a search based on the query across all three models
        shoe_results = Shoe.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        cloth_results = Cloth.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        electronic_results = Electronic.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

        # Combine the results from all three models
        results = list(shoe_results) + list(cloth_results) + \
            list(electronic_results)
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

    for image in images:
        # Create a ProductImage object, associate it with the product, and save it
        product_image = ProductImage.objects.create(
            content_object=product, image=image)

        product_image.object_id = product.pk
        product_image.save()


@login_required(login_url="login")
def add_product(request):
    message = ""
    category = request.POST.get('category')
    print("category: ", category)
    if request.method == 'POST':
        if category == "Shoe":
            # category = "Shoe"
            form = ShoeForm(request.POST, request.FILES)
        elif category == "Cloth":
            # category = "Cloth"
            form = ClothForm(request.POST, request.FILES)
        elif category == "Electronic":
            # category = "Electronic"
            form = ElectronicForm(request.POST, request.FILES)
        else:
            # This shouldn't happen, but handle it just in case
            return redirect('manager')

        images = request.FILES.getlist("images")
        print("images: ", images)
        if form.is_valid():
            # Save the product information
            product = form.save()

            # Handle product images using the extracted method
            # handle_product_images(product, images, request)

            handle_product_images(product, images, request)

            if images:
                first_image = images[0]
                print("first image is: ", first_image)
                product.image = first_image.name
                print("Product Fields:")
                print("ID:", product.id)
                print("Name:", product.name)
                print("Description:", product.description)
                print("Image:", product.image)
                product.save()

            # Handle successful product creation
            message = "success"
            return redirect('add_product')
        else:
            print("wont submit form: ")

    else:
        # If the request method is not POST, show the shoe form by default
        print("somehow here I am ")
        # form = ShoeForm()
        return redirect('manager')

    context = {'form': form, 'message': message, 'category': category}
    return render(request, 'forms/add_product.html', context)
