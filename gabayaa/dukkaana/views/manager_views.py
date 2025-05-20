from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
# from ..models import Cloth, Shoe, Electronic, ProductImage
# from ..forms import ProductForm, ShoeForm, ClothForm, ElectronicForm
from ..models import ProductImage, Product, Customer, Order, OrderItem, PromoCode
from ..forms import ProductForm, PromoCodeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from .helper import superuser_required


# @login_required(login_url="login")


@superuser_required
def view_products(request):
    cloth_products = Product.objects.filter(category='Huccuu')
    shoe_products = Product.objects.filter(category='Kophee')
    electronic_products = Product.objects.filter(category='Electrooniksii')
    print(electronic_products)

    context = {
        'cloth_products': cloth_products,
        'shoe_products': shoe_products,
        'electronic_products': electronic_products,
    }

    return render(request, 'auth/view_products.html', context)


# @login_required(login_url="login")
@superuser_required
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


# @login_required(login_url="login")
@superuser_required
def search_customer(request):
    query = request.GET.get('q')  # Get the search query from the request

    if query:
        # Perform a search based on the query across all three models
        product = Customer.objects.filter(
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

    return render(request, 'customer_list.html', context)


# saves images and connect to right item through its primary key
# @login_required(login_url="login")
# @superuser_required
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


# @login_required(login_url="login")
@superuser_required
def add_product(request):
    message = ""
    category = request.POST.get('category')
    print("category: ", category)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")

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
        else:
            if 'submit' in request.POST:
                print("wont submit form: ")
                messages.error(
                    request, 'failed to add new product. try again!')
    else:
        return redirect("manager")

    context = {'form': form, 'message': message, 'category': category}
    return render(request, 'forms/add_product.html', context)


# @login_required(login_url="login")
@superuser_required
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


# @login_required(login_url="login")
@superuser_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'successfully deleted the product')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # Redirect to the search page in case of a GET request
    return redirect("search_product")


# @login_required(login_url="login")
@superuser_required
def customer_list(request):
    customers = Customer.objects.all()
    context = {'customers': customers}
    return render(request, 'auth/customer_list.html', context)


# @login_required(login_url="login")
@superuser_required
def customer_search(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.filter(username__icontains=query)
    # You can filter customers based on your search criteria
    data = [{'id': customer.id, 'username': customer.username,
             'is_superuser': customer.is_superuser} for customer in customers]
    return JsonResponse({'customers': data})

# @login_required(login_url="login")


@superuser_required
def order_list(request):
    query = request.GET.get('q', '')

    if query:
        orders = Order.objects.filter(user__icontains=query)
    else:
        orders = Order.objects.all()

    context = {
        'orders': orders,
    }

    return render(request, 'auth/order_list.html', context)

# @login_required(login_url="login")


# @superuser_required
def perform_order_search(query):
    # Perform search based on the user field
    print("were searching: ", query)
    results = []

    if query:
        orders = Order.objects.filter(user__icontains=query)
        for order in orders:
            items = OrderItem.objects.filter(order=order)
            results.append((order, items))

    return results

# @login_required(login_url="login")


@superuser_required
def order_search(request):
    # Get the search query parameter from the request
    q = request.GET.get('q', '')

    # Fetch all orders or perform the search if a query is provided
    if q:
        print("search: ", q)
        results = perform_order_search(q)
        print("great searched it: ")
        orders = [order for order, items in results]
    else:
        orders = Order.objects.all()

    # Prepare the data to be returned as JSON
    data = []
    for order in orders:
        order_data = {
            'id': order.id,
            'user': order.user,
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'total_amount': float(order.total_amount),
            'shipping_address': order.shipping_address,
            'status': order.status,
            'items': []
        }
        # Add items for the order
        items = OrderItem.objects.filter(order=order)
        for item in items:
            order_data['items'].append({
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': float(item.price)
            })
        data.append(order_data)

    # Return the data as JSON
    return JsonResponse(data, safe=False)


# To allow POST request without CSRF token (for simplicity, use proper authentication in production)
@csrf_exempt
# @login_required(login_url="login")
@superuser_required
def update_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')

        try:
            order = Order.objects.get(pk=order_id)
            order.status = new_status
            order.save()
            return JsonResponse({'message': 'Order status updated successfully'})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@superuser_required
def create_promo_code(request):
    if request.method == 'POST':
        form = PromoCodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Promo code created successfully.')
            return redirect('manager')
    else:
        form = PromoCodeForm()
    return render(request, 'auth/create_promo_code.html', {'form': form})

#  export PATH="/Users/gammachis/Desktop/flutter/bin"
