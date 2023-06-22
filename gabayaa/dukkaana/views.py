from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Cloth, Shoe, Electronic
from .forms import ProductForm, ShoeForm, ClothForm, ElectronicForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.backends.db import SessionStore
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal

from django.http import JsonResponse
from django.conf import settings
from django import template
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

register = template.Library()


@register.filter
def get_filename(value):
    return value.split('/')[-1]

# def checkout(request):
#     YOUR_DOMAIN = 'http://127.0.0.1:8000'
#     checkout_session = stripe.checkout.Session.create(
#         line_items=[
#             {
#                 # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                 'price': 'price_1NGHhHFMdMB6ZhbsQwsfub3C',
#                 'quantity': 1,
#             },
#         ],
#         mode='payment',
#         success_url=YOUR_DOMAIN + '/success',
#         cancel_url=YOUR_DOMAIN + '/cancel',
#     )
#     # return JsonResponse({'id': checkout_session.id})
#     return redirect(checkout_session['url'], code=303)


def checkout(request):
    YOUR_DOMAIN = 'http://127.0.0.1:8000/checkout'
    cart = request.session.get('cart', {})
    line_items = []
    for item_id, item in cart.items():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                # Stripe accepts prices in cents
                'unit_amount': int(item['price'] * 100),
                'product_data': {
                    'name': item['name'],
                },
            },
            'quantity': item['quantity'],
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=YOUR_DOMAIN + '/success',
        cancel_url=YOUR_DOMAIN + '/cancel',
    )

    # return JsonResponse({'sessionId': session.id})
    return redirect(session['url'], code=303)


def checkout_success(request):
    # prepare the confirmation with relevant details abuot the order
    # create order model with customer details (name, contact,), items (cart), placed date

    # Clear the cart after successful checkout
    request.session['cart'] = {}
    return render(request, 'success.html')


def checkout_cancel(request):
    return render(request, 'cancel.html')


def base(request):
    username = request.GET.get('username')
    return render(request, 'base.html', {'username': username})


def cloths(request):
    # cloths = Cloth.objects.all()
    products = Cloth.objects.all()
    return render(request, 'view/products.html', {'products': products})


def shoes(request):
    # shoes = Shoe.objects.all()
    products = Shoe.objects.all()
    return render(request, 'view/products.html', {'products': products})


def electronics(request):
    # electronics = Electronic.objects.all()
    products = Electronic.objects.all()
    return render(request, 'view/products.html', {'products': products})


def renting(request):
    return render(request, 'renting.html', {})


def buying(request):
    return render(request, 'buying.html', {})


def product_info(request, category, id):

    print("------------d in here: ", id)
    product = None
    print("this is: ", category)
    if category == 'Shoe':
        # Logic to retrieve shoe product based on product_id
        product = Shoe.objects.get(id=id)
    elif category == 'Cloth':
        # Logic to retrieve cloth product based on product_id
        product = Cloth.objects.get(id=id)
    elif category == 'Electronic':
        # Logic to retrieve electronic product based on product_id
        product = Electronic.objects.get(id=id)
    if product:
        # Render the product information in a template
        return render(request, 'view/product_info.html', {'product': product})
    else:
        return HttpResponse('Product not found')


@login_required(login_url="login")
def manager(request):
    if request.user.is_authenticated:
        # username = request.session['username']
        print("success")
        print("username that is authenticated:", request.user)
        return render(request, 'manager/manager.html', {})

    print("back to login")
    return redirect('login')


def logoutManager(request):
    logout(request)
    return redirect("login")


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


def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Registration successful. Please log in.')
            # return redirect('login')
        else:
            messages.error(request, 'Invalid form. Please correct the errors.')
    else:
        print("request method is get")
    context = {'form': form}
    return render(request, 'manager/register.html', context)


def loginManager(request):
    if request.method == 'POST':
        print("valid form ")
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            print("here")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # request.session['managerLogin'] = True
                # request.session['username'] = username
                print("user that logged in ", request.user)
                return redirect('manager')
            else:
                print("user is NONE")
    else:
        print("invlaid form ")

        form = AuthenticationForm()
        messages.error(request, 'Invalid form. Please correct the errors.')

    context = {'form': form}
    return render(request, 'manager/login.html', context)


@login_required(login_url="login")
def add_shoe(request):

    message = None

    form = ShoeForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        message = "successfully added shoe!"
        return redirect('manager')
    else:
        # Handle invalid shoe form
        message = "Shoe form is invalid! Please correct the errors in the form."
        # print(form.errors)
    form = ShoeForm()

    context = {'form': form, 'message': message}
    return render(request, 'forms/add_shoe.html', context)


@login_required(login_url="login")
def add_cloth(request):
    message = None

    form = ClothForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        # Handle successful cloth creation
        return redirect('manager')
    else:
        # Handle invalid cloth form
        message = "Cloth form is invalid! Please correct the errors in the form."

    form = ClothForm()
    context = {'form': form, 'message': message}
    return render(request, 'forms/add_cloth.html', context)


@login_required(login_url="login")
def add_electronic(request):
    form = ElectronicForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        # Handle successful electronic creation
        return redirect('manager')
    else:
        # Handle invalid electronic form
        message = "Electronic form is invalid! Please correct the errors in the form."

    form = ElectronicForm()
    context = {'form': form, 'message': message}
    return render(request, 'forms/add_electronic.html', context)


# class DecimalEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Decimal):
#             return str(obj)
#         return super().default(obj)


def calculate_item_count(cart):
    item_count = 0
    for item_id, item in cart.items():
        quantity = item.get('quantity')
        item_count += quantity
    return item_count


def cart(request):
    cart = []
    item_count = 0
    # if request.user.is_authenticated:
    #     cart = request.user.cart
    # else:
    cart = request.session.get('cart', {})

    # Calculate the total price
    total_price = 0.0
    for item_id, item in cart.items():
        price = item.get('price')
        quantity = item.get('quantity')
        item_total = price * quantity
        total_price += item_total

    # Add the total price to the cart session
    request.session['total_price'] = total_price

    item_count = calculate_item_count(cart)
    context = {'cart': cart, 'item_count': item_count,
               'total_price': total_price}
    return render(request, 'cart.html', context)


def add_to_cart(request, category, id):
    session_key = request.session.session_key
    if not session_key:
        request.session.cycle_key()
        session_key = request.session.session_key

    print("Product being added to cart is:", category)

    if category == 'Shoe':
        product = Shoe.objects.get(id=id)
    elif category == 'Cloth':
        product = Cloth.objects.get(id=id)
    elif category == 'Electronic':
        product = Electronic.objects.get(id=id)

    if product:
        cart = request.session.get('cart', {})
        cart_key = f"{category}_{product.id}"
        cart_item = {
            'custom_id': cart_key,
            'id': product.id,
            'category': category,
            'name': product.name,
            'quantity': 1,
            'price': product.price,
            'image': str(product.image),
        }
        cart[cart_key] = cart_item
        request.session['cart'] = cart
        messages.success(request, 'item successfully added to cart!')
        return redirect(request.META['HTTP_REFERER'])

    else:
        messages.error(
            request, 'IDK what went wrong sorry couldnt add item to cart :(')
    cart = []
    request.session['cart'] = cart
    return redirect(request.META['HTTP_REFERER'])


def increase_quantity(request, id):
    if 'cart' in request.session:
        cart = request.session['cart']
        if id in cart:
            cart[id]['quantity'] += 1
            request.session.modified = True
        else:
            messages.error(request, 'error increasing quantity!')
    return redirect('cart')


def decrease_quantity(request, id):
    if 'cart' in request.session:

        cart = request.session['cart']
        if id in cart:
            quantity = cart[id]['quantity']
            print("before ", quantity)

            if (quantity == 1):
                print(" deleted item ")
                remove_cart_item(request, id)
                return redirect('cart')

            cart[id]['quantity'] -= 1
            request.session.modified = True
        else:
            messages.error(request, 'item to decrease quantity not found!')
    return redirect('cart')


def edit_quantity(request, id):
    if request.method == "POST":
        quantity = int(request.POST.get('item' + id))
        print("quantity here: ", quantity)
        if (quantity < 0):
            messages.error(request, 'quantity cannot be less than 0!')
        elif (quantity == 0):
            remove_cart_item(request, id)
        else:
            cart = request.session.get('cart', {})
            if id in cart:
                cart[id]['quantity'] = quantity
                request.session['cart'] = cart
                # messages.success(
                #     request, 'successfully updated quantity')
            else:
                print("this item: ", id)
                messages.error(
                    request, 'error decreasing quantity because it doesnt exist!')
    else:
        messages.error(
            request, 'error editing quantity because its not post method!')
    return redirect('cart')


def remove_cart_item(request, id):
    # Retrieve the cart from the session
    cart = request.session.get('cart', {})

    removed_item = cart[id]
    print("----------id: ", id)
    if id in cart:

        del cart[id]  # Remove the item from the cart
        # print("successfully removed", removed_item['name'])
        messages.success(request, 'item successfully removed from cart!')
    else:
        messages.error(request, 'error in removing the item')
        print(removed_item['name'], "is not removed")

    request.session['cart'] = cart  # Update the cart in the session

    return redirect('cart')  # Redirect to the
