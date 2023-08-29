from django.shortcuts import render, redirect
from .helper import calculate_item_count, convertToDict
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from ..models import Product, CartItem, Cart
from django.contrib import messages
import json


def cart(request):
    total_price = 0.0
    cart = {}
    if request.user.is_authenticated:
        # If the user is logged in, get their user-specific cart from the database
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=user_cart)
        item_count = user_cart.total_items
        total_price = round(user_cart.total_price, 2)
        cart = cart_items
        context = {'cart': cart, 'item_count': item_count,
                   'total_price': total_price}
        return render(request, 'mycart.html', context)
    else:
        # request.session['cart'] = {}
        cart_json = request.session.get('cart', {})
        print("cart_json:", cart_json)
        cart = convertToDict(cart_json)

        # Calculate the total price
        for item_id, item in cart.items():
            price = item.get('price')
            quantity = item.get('quantity')
            item_total = price * quantity
            total_price += round(item_total, 2)

        # Add the total price to the cart session
        request.session['total_price'] = total_price

        item_count = calculate_item_count(cart)

    context = {'cart': cart, 'item_count': item_count,
               'total_price': total_price}

    request.session['from_cart'] = True

    return render(request, 'cart.html', context)


def update_cart_totals(cart):
    cart_items = CartItem.objects.filter(cart=cart)
    cart.total_items = cart_items.aggregate(total_items=Sum('quantity'))[
        'total_items'] or 0
    cart.total_price = sum(item.get_total_price() for item in cart_items)
    cart.save()


def update_cart_quantity(cart):
    # Calculate the total_items by summing the quantities of all cart items
    total_items = CartItem.objects.filter(
        cart=cart).aggregate(Sum('quantity'))['quantity__sum']

    # Calculate the total_price by summing the product of quantity and product price
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price *
                      item.quantity for item in cart_items)

    # Update the cart's total_items and total_price fields
    cart.total_items = total_items if total_items else 0
    cart.total_price = total_price if total_price else 0
    cart.save()


def add_to_cart(request, category, id):
    if request.user.is_authenticated:
        # Get the product
        product = get_object_or_404(Product, id=id)

        # Get the user's cart or create one if it doesn't exist
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is already in the cart
        cart_item, cart_item_created = CartItem.objects.get_or_create(
            cart=cart, product=product)

        if not cart_item_created:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item.unit_price = product.price
            cart_item.save()

        # Update the total_items and total_price fields in the cart
        update_cart_totals(cart)
        messages.success(request, 'item successfully added to cart!')

    else:
        product = Product.objects.get(id=id)
        if product:
            # request.session['cart'] = {}
            cart_json = request.session.get('cart', {})
            cart = convertToDict(cart_json)
            cart_key = product.id
            # cart_key = f"{category}_{product.id}"

            cart_item = {
                'id': cart_key,
                # 'id': product.id,
                'category': category,
                'name': product.name,
                'quantity': 1,
                'price': float(product.price),
                'image': product.image,
                # 'image': str(product.image),
            }
            print("cart_json: ", cart_json)
            print("just added now: ", cart_item)
            print("cart: ", cart)
            cart[cart_key] = cart_item
            cart_json = json.dumps(cart)
            request.session['cart'] = cart_json
            messages.success(request, 'item successfully added to cart!')
        else:
            messages.error(
                request, 'IDK what went wrong sorry couldnt add item to cart :(')
        # request.session['cart'] = cart
    return redirect(request.META['HTTP_REFERER'])


def increase_quantity(request, id):

    if request.user.is_authenticated:
        print("trying to increase auth user quantity")

        product = get_object_or_404(Product, id=id)
        cart = Cart.objects.get(user=request.user)

        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product)

        # Increment the quantity of the cart item and save it
        cart_item.quantity += 1
        cart_item.save()
        print("product: ", product)
        print("cart: ", cart)
        print("cart item: ", cart_item)
        update_cart_quantity(cart)
    else:
        if 'cart' in request.session:
            cart_json = request.session['cart']
            # Parse the cart JSON string into a dictionary
            cart = convertToDict(cart_json)
            if id in cart:
                cart[id]['quantity'] += 1
                # Convert the updated cart dictionary back to a JSON string
                cart_json = json.dumps(cart)
                request.session['cart'] = cart_json
            else:
                messages.error(request, 'Error increasing quantity!')
    return redirect('cart')


def decrease_quantity(request, id):
    if request.user.is_authenticated:
        print("trying to decrease auth user quantity")

        product = get_object_or_404(Product, id=id)
        cart = Cart.objects.get(user=request.user)

        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product)
        if cart_item.quantity == 1:
            cart_item.delete()
            update_cart_quantity(cart)
        else:
            print("quantity before decrease: ", cart_item.quantity)
            # Increment the quantity of the cart item and save it
            cart_item.quantity -= 1
            cart_item.save()
            print("product: ", product)
            print("cart: ", cart)
            print("cart item: ", cart_item)
            update_cart_quantity(cart)
    else:
        if 'cart' in request.session:
            cart_json = request.session['cart']
            cart = convertToDict(cart_json)
            if id in cart:
                if (cart[id]['quantity'] == 1):
                    print(" deleted item ")
                    remove_cart_item(request, id)
                    return redirect('cart')

                cart[id]['quantity'] -= 1
                cart_json = json.dumps(cart)
                request.session['cart'] = cart_json
            else:
                messages.error(request, 'item to decrease quantity not found!')
    return redirect('cart')


def edit_quantity(request, id):
    # if request.method == "POST":
    new_quantity = int(request.POST.get('item' + id))
    print("quantity here: ", new_quantity)
    print("were editing: ", id)

    if request.user.is_authenticated:
        if new_quantity == 0:
            remove_cart_item(request, id)
        elif new_quantity < 0:
            print("cant do that")
        else:
            product = get_object_or_404(Product, id=id)
            cart = Cart.objects.get(user=request.user)

            # Check if the product is already in the cart
            cart_item = CartItem.objects.get(
                cart=cart, product=product)

            # Increment the quantity of the cart item and save it
            cart_item.quantity = new_quantity
            cart_item.save()
            update_cart_quantity(cart)
    else:
        if (new_quantity < 0):
            messages.error(request, 'quantity cannot be less than 0!')
        elif (new_quantity == 0):
            remove_cart_item(request, id)
        else:
            cart_json = request.session['cart']
            cart = convertToDict(cart_json)
            if id in cart:
                cart[id]['quantity'] = new_quantity
                request.session['cart'] = cart
            else:
                print("this item: ", id)
                messages.error(
                    request, 'error decreasing quantity because it doesnt exist!')
    return redirect('cart')


def remove_cart_item(request, id):
    # Retrieve the cart from the session
    if request.user.is_authenticated:
        print("lets remove item")

        product = get_object_or_404(Product, id=id)
        cart = Cart.objects.get(user=request.user)

        # Check if the product is already in the cart
        cart_item = CartItem.objects.get(
            cart=cart, product=product)
        cart_item.delete()
        update_cart_quantity(cart)
    else:
        cart_json = request.session.get('cart', {})
        cart = convertToDict(cart_json)
        removed_item = cart[id]
        print("----------id: ", id)
        if id in cart:
            del cart[id]  # Remove the item from the cart
            messages.success(request, 'item successfully removed from cart!')
        else:
            messages.error(request, 'error in removing the item')
            print(removed_item['name'], "is not removed")

        cart_json = json.dumps(cart)
        request.session['cart'] = cart_json  # Update the cart in the session

    return redirect('cart')  # Redirect to the
