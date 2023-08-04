from django.shortcuts import render, redirect
from .helper import calculate_item_count, convertToDict
from ..models import Cloth, Shoe, Electronic
from django.contrib import messages
import json


def cart(request):
    cart = []
    item_count = 0
    # if request.user.is_authenticated:
    #     cart = request.user.cart
    # else:
    cart_json = request.session.get('cart', {})
    cart = convertToDict(cart_json)

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
        cart_json = request.session.get('cart', {})
        cart = convertToDict(cart_json)
        cart_key = f"{category}_{product.id}"

        # Retrieve all images related to this product using the generic foreign key
        # images = ProductImage.objects.filter(
        #     content_type__model=category.lower(), object_id=product.pk)
        # image_urls = [str(image.image) for image in images]

        # image = ProductImage.objects.filter(
        #     content_type__model=category.lower(), object_id=product.pk).first()
        # image_url = str(image.image)

        cart_item = {
            'custom_id': cart_key,
            'id': product.id,
            'category': category,
            'name': product.name,
            'quantity': 1,
            'price': product.price,
            'image': product.image,
            # 'image': str(product.image),
        }
        cart[cart_key] = cart_item
        print("just added now: ", cart_item)
        cart_json = json.dumps(cart)
        request.session['cart'] = cart_json
        messages.success(request, 'item successfully added to cart!')
        return redirect(request.META['HTTP_REFERER'])

    else:
        messages.error(
            request, 'IDK what went wrong sorry couldnt add item to cart :(')
    # cart = []
    request.session['cart'] = cart
    return redirect(request.META['HTTP_REFERER'])


def increase_quantity(request, id):
    if 'cart' in request.session:
        cart_json = request.session['cart']
        # Parse the cart JSON string into a dictionary
        cart = convertToDict(cart_json)
        if id in cart:
            cart[id]['quantity'] += 1
            # Convert the updated cart dictionary back to a JSON string
            cart_json = json.dumps(cart)
            request.session['cart'] = cart_json
            request.session.modified = True
        else:
            messages.error(request, 'Error increasing quantity!')
    return redirect('cart')


def decrease_quantity(request, id):
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
            cart_json = request.session['cart']
            cart = convertToDict(cart_json)
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

    cart_json = request.session.get('cart', {})
    cart = convertToDict(cart_json)
    removed_item = cart[id]
    print("----------id: ", id)
    if id in cart:

        del cart[id]  # Remove the item from the cart
        # print("successfully removed", removed_item['name'])
        messages.success(request, 'item successfully removed from cart!')
    else:
        messages.error(request, 'error in removing the item')
        print(removed_item['name'], "is not removed")

    cart_json = json.dumps(cart)
    request.session['cart'] = cart_json  # Update the cart in the session

    return redirect('cart')  # Redirect to the


# keep cart based on session
# add cart based on  database associated with the buyers
