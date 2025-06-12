from types import SimpleNamespace
from django.shortcuts import render, redirect, get_object_or_404
from .helper import calculate_item_count, convertToDict
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from ..models import Product, CartItem, Cart, PromoCode
from django.contrib import messages
import json
from django.http import JsonResponse
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from ..constants import TRANSACTION_FEE_PERCENTAGE
from ..utils.cart import CartSummary

TRANSACTION_FEE_PERCENTAGE = Decimal('0.03')


def normalize_cart(cart_items):
    """
    Normalize the cart data structure so that it has the same fields for both
    authenticated and non-authenticated users.
    """
    normalized_cart = {}
    for cart_item in cart_items:
        id = cart_item.product.id  # Assuming the product has an ID field
        price = cart_item.product.price  # Assuming the product has a price field
        quantity = cart_item.quantity
        image = cart_item.product.image
        name = cart_item.product.name
        category = cart_item.product.category
        normalized_cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': quantity,
            'category': category,
            'image': image,
        }
    return normalized_cart


def get_or_create_cart(request):
    """
    Helper function to get or create a cart for the current user.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    return None


def get_session_cart(request):
    """
    Helper function to get the cart from session.
    """
    cart_json = request.session.get('cart', '{}')
    return convertToDict(cart_json)


def update_session_cart(request, cart):
    """
    Helper function to update the cart in session.
    """
    request.session['cart'] = json.dumps(cart)


def view_cart(request):
    """
    View to display the shopping cart.
    """
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
        except Cart.DoesNotExist:
            cart_items = []
    else:
        session_cart = get_session_cart(request)
        cart_items = []
        for item_id, item_data in session_cart.items():
            try:
                product = Product.objects.get(id=item_id)
                cart_items.append(SimpleNamespace(
                    id=item_id,
                    product=product,
                    quantity=item_data['quantity'],
                    unit_price=product.price
                ))
            except Product.DoesNotExist:
                continue

    summary = CartSummary(cart_items)

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'cart_summary': summary.to_dict()
    })


def add_to_cart(request, product_id):
    """
    View to add a product to the cart (supports both authenticated and guest users).
    """
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'unit_price': product.price}
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            cart.update_totals()
        else:
            cart = get_session_cart(request)
            pid = str(product_id)
            print(f"pid: {pid}")
            if pid in cart:
                cart[pid]['quantity'] += 1
            else:
                cart[pid] = {
                    'id': pid,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': 1,
                    'category': product.category,
                    'image': str(product.get_first_image().image.url) if product.get_first_image() else '',
                }
            print("bout to update session cart")
            update_session_cart(request, cart)
            print("updated session cart")
        messages.success(request, _('Product added to cart successfully.'))
        print("added to cart")
        # Redirect to the product detail page after adding to cart
        return redirect('product_detail', id=product_id)
    except Exception as e:
        print(f"[ERROR] Exception in add_to_cart: {e}")
        messages.error(request, _(
            'An error occurred while adding the product to your cart.'))
        return render(request, 'error.html', {
            'error_message': _('An error occurred while adding the product to your cart.')
        })


@require_POST
def update_cart_item(request, item_id):
    """
    View to update cart item quantity.
    """
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))

        if request.user.is_authenticated:
            cart_item = get_object_or_404(
                CartItem, id=item_id, cart__user=request.user)
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart = get_session_cart(request)
            if str(item_id) in cart:
                cart[str(item_id)]['quantity'] = quantity
                request.session['cart'] = json.dumps(cart)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def remove_cart_item(request, item_id):
    """
    View to remove item from cart.
    """
    try:
        if request.user.is_authenticated:
            try:
                cart_item = CartItem.objects.get(
                    id=item_id, cart__user=request.user)
                cart_item.delete()
            except CartItem.DoesNotExist:
                return JsonResponse({'success': True})  # Item already removed
        else:
            cart = get_session_cart(request)
            if str(item_id) in cart:
                del cart[str(item_id)]
                request.session['cart'] = json.dumps(cart)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def proceed_to_checkout(request):
    """
    View to handle proceeding to checkout from cart.
    """
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        if not CartItem.objects.filter(cart=cart).exists():
            messages.warning(request, _('Your cart is empty.'))
            return redirect('cart')
    else:
        cart = get_session_cart(request)
        if not cart:
            messages.warning(request, _('Your cart is empty.'))
            return redirect('cart')

    # Set session flag to indicate coming from cart
    request.session['from_cart'] = True
    return redirect('process_checkout')


def update_total_after_discount(request):
    new_total = float(request.POST.get('total'))
    discount_percent = float(request.POST.get('discount_percent'))
    print(" total before", request.session['total'])
    request.session['total'] = new_total

    request.session['discount_percent'] = discount_percent
    print("updated total", new_total)
    return JsonResponse({'message': 'updated total and discouont_percentage successfully'})


@require_POST
def update_quantity(request, id, action):
    """
    View to update the quantity of an item in the cart.
    """
    try:
        if request.user.is_authenticated:
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=id)

            if action == 'increase':
                cart_item.quantity += 1
            elif action == 'decrease' and cart_item.quantity > 1:
                cart_item.quantity -= 1
            elif action == 'decrease':
                cart_item.delete()
                cart.update_totals()
                return redirect('cart')

            cart_item.save()
            cart.update_totals()
        else:
            cart = get_session_cart(request)
            if id in cart:
                if action == 'increase':
                    cart[id]['quantity'] += 1
                elif action == 'decrease' and cart[id]['quantity'] > 1:
                    cart[id]['quantity'] -= 1
                elif action == 'decrease':
                    del cart[id]

                update_session_cart(request, cart)

        return redirect('cart')

    except Exception as e:
        messages.error(request, _(
            'An error occurred while updating the quantity.'))
        return redirect('cart')


def apply_promo_code(request):
    """
    View to apply a promo code to the cart.
    """
    try:
        code = request.POST.get('promo_code', '').strip()
        if not code:
            return JsonResponse({
                'success': False,
                'message': _('Please enter a promo code.')
            })

        promo = get_object_or_404(PromoCode, code=code, is_active=True)

        if not promo.is_valid():
            return JsonResponse({
                'success': False,
                'message': _('This promo code is no longer valid.')
            })

        if request.user.is_authenticated:
            cart = get_or_create_cart(request)
            if cart.total_price < promo.min_order_value:
                return JsonResponse({
                    'success': False,
                    'message': _('Minimum order value not met for this promo code.')
                })

            cart.promo_code = promo
            cart.update_totals()

            return JsonResponse({
                'success': True,
                'message': _('Promo code applied successfully.'),
                'discount': float(promo.discount),
                'new_total': float(cart.total_price)
            })
        else:
            cart = get_session_cart(request)
            subtotal = sum(item['price'] * item['quantity']
                           for item in cart.values())

            if subtotal < promo.min_order_value:
                return JsonResponse({
                    'success': False,
                    'message': _('Minimum order value not met for this promo code.')
                })

            discount = subtotal * (promo.discount / 100)
            new_total = subtotal - discount

            return JsonResponse({
                'success': True,
                'message': _('Promo code applied successfully.'),
                'discount': float(promo.discount),
                'new_total': float(new_total)
            })

    except PromoCode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': _('Invalid promo code.')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': _('An error occurred while applying the promo code.')
        })


def get_promo(request):
    """
    View to get the promo code.
    """
    return render(request, 'get_promo.html')


def increase_quantity(request, id):
    """
    View to increase the quantity of an item in the cart.
    """
    try:
        if request.user.is_authenticated:
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=id)
            cart_item.quantity += 1
            cart_item.save()
            cart.update_totals()
        else:
            cart = get_session_cart(request)
            if id in cart:
                cart[id]['quantity'] += 1
                update_session_cart(request, cart)

        return redirect('cart')

    except Exception as e:
        messages.error(request, _(
            'An error occurred while increasing the quantity.'))
        return redirect('cart')


def decrease_quantity(request, id):
    """
    View to decrease the quantity of an item in the cart.
    """
    try:
        if request.user.is_authenticated:
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                cart.update_totals()
        else:
            cart = get_session_cart(request)
            if id in cart:
                if cart[id]['quantity'] > 1:
                    cart[id]['quantity'] -= 1
                    update_session_cart(request, cart)

        return redirect('cart')

    except Exception as e:
        messages.error(request, _(
            'An error occurred while decreasing the quantity.'))
        return redirect('cart')


def edit_quantity(request, id):
    """
    View to edit the quantity of an item in the cart.
    """
    try:
        if request.user.is_authenticated:
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=id)
            new_quantity = int(request.POST.get('quantity'))
            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()
                cart.update_totals()
        else:
            cart = get_session_cart(request)
            if id in cart:
                cart[id]['quantity'] = int(request.POST.get('quantity'))
                update_session_cart(request, cart)

        return redirect('cart')

    except Exception as e:
        messages.error(request, _(
            'An error occurred while editing the quantity.'))
        return redirect('cart')


@require_POST
def clear_cart(request):
    """
    View to clear all items from the cart.
    """
    try:
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            CartItem.objects.filter(cart=cart).delete()
            cart.update_totals()
        else:
            request.session['cart'] = '{}'
            request.session['total'] = 0
            request.session['discount_percent'] = 0

        messages.success(request, _('Your cart has been cleared.'))
        return redirect('cart')
    except Exception as e:
        messages.error(request, _(
            'An error occurred while clearing your cart.'))
        return redirect('cart')
