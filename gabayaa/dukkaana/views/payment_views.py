from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
import uuid
import stripe
import requests
from decimal import Decimal
from ..models import Product, CartItem, Cart, Order, OrderItem, PromoCode
from .cart_views import get_session_cart, calculate_cart_totals

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_stripe_line_items(cart_items, promo_discount=None):
    """
    Helper function to create line items for Stripe checkout.
    """
    line_items = []
    for item in cart_items:
        if isinstance(item, CartItem):
            price = item.unit_price
            name = item.product.name
            quantity = item.quantity
        else:
            price = item['price']
            name = item['name']
            quantity = item['quantity']

        if promo_discount:
            price = price * (1 - Decimal(promo_discount))

        # Add transaction fee
        price = price * Decimal('1.03')
        price = int(round(price * 100))  # Convert to cents

        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': price,
                'product_data': {
                    'name': name,
                },
            },
            'quantity': quantity,
        })
    return line_items


def stripe_checkout(request):
    """
    View to handle Stripe checkout.
    """
    try:
        if not request.session.get('from_cart', False):
            messages.warning(request, _(
                'Please review your cart before checkout.'))
            return redirect('cart')

        YOUR_DOMAIN = request.build_absolute_uri('/checkout')
        promo_discount = request.session.get('promo_discount', '0.00')

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
            line_items = get_stripe_line_items(cart_items, promo_discount)
        else:
            cart = get_session_cart(request)
            line_items = get_stripe_line_items(cart.values(), promo_discount)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
            customer_email=request.user.email if request.user.is_authenticated else None,
            metadata={
                'user_id': str(request.user.id) if request.user.is_authenticated else 'guest',
                'promo_code': request.session.get('promo_code', ''),
            }
        )

        request.session['from_checkout'] = True
        return redirect(session.url, code=303)

    except Exception as e:
        messages.error(request, _(
            'An error occurred during checkout. Please try again.'))
        return redirect('cart')


def get_paypal_access_token():
    """
    Helper function to get PayPal access token.
    """
    try:
        url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US'
        }
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(
            url,
            headers=headers,
            data=data,
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
        )
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        raise Exception(_('Failed to get PayPal access token'))


def paypal_checkout(request):
    """
    View to handle PayPal checkout.
    """
    try:
        if not request.session.get('from_cart', False):
            messages.warning(request, _(
                'Please review your cart before checkout.'))
            return redirect('cart')

        host = request.get_host()
        promo_discount = request.session.get('promo_discount', '0.00')

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
            item_details = [{
                'name': item.product.name,
                'price': str(item.unit_price),
                'quantity': item.quantity,
            } for item in cart_items]
            total_price = cart.total_price
            item_total = cart.total_items
        else:
            cart = get_session_cart(request)
            item_details = [{
                'name': item['name'],
                'price': str(item['price']),
                'quantity': item['quantity'],
            } for item in cart.values()]
            total_price = request.session.get('total_price', 0)
            item_total = sum(item['quantity'] for item in cart.values())

        # Apply promo discount if exists
        if promo_discount:
            total_price = total_price * (1 - Decimal(promo_discount))

        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': str(total_price),
            'item_name': 'Order',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'USD',
            'notify_url': f'http://{host}{reverse("paypal-ipn")}',
            'return_url': f'http://{host}{reverse("success")}',
            'cancel_url': f'http://{host}{reverse("cancel")}',
            'item_total': item_total,
            'items': item_details,
            'custom': str(request.user.id) if request.user.is_authenticated else 'guest',
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        request.session['from_checkout'] = True

        context = {
            "form": form,
            "cart": cart,
            "total_price": total_price,
            'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID
        }
        return render(request, 'paypal_checkout.html', context)

    except Exception as e:
        messages.error(request, _(
            'An error occurred during PayPal checkout. Please try again.'))
        return redirect('cart')


@receiver(valid_ipn_received)
def paypal_payment_notification(sender, **kwargs):
    """
    Signal handler for PayPal IPN notifications.
    """
    ipn_obj = sender
    if ipn_obj.payment_status == "Completed":
        try:
            order = Order.objects.get(invoice=ipn_obj.invoice)
            order.payment_status = 'Paid'
            order.save()

            # Send confirmation email
            send_mail(
                _('Order Confirmation'),
                _('Thank you for your order! Your order has been received and is being processed.'),
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email if hasattr(
                    order.user, 'email') else ipn_obj.payer_email],
                fail_silently=True,
            )
        except Order.DoesNotExist:
            pass


def create_order(request, payment_method, payment_status='Pending'):
    """
    Helper function to create an order.
    """
    try:
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
            total_price = cart.total_price
            shipping_address = f"{request.user.street_address}, {request.user.city}, {request.user.state}, {request.user.zip_code}"

            order = Order.objects.create(
                user=request.user,
                total_amount=total_price,
                shipping_address=shipping_address,
                payment_method=payment_method,
                payment_status=payment_status,
                status='Pending'
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.unit_price
                )

            cart.delete()
        else:
            cart = get_session_cart(request)
            total_price = request.session.get('total_price', 0)
            shipping_address = request.session.get(
                'shipping_address', 'Guest address')

            order = Order.objects.create(
                user="guest",
                total_amount=total_price,
                shipping_address=shipping_address,
                payment_method=payment_method,
                payment_status=payment_status,
                status='Pending'
            )

            for item in cart.values():
                OrderItem.objects.create(
                    order=order,
                    product_name=item['name'],
                    quantity=item['quantity'],
                    price=item['price']
                )

            request.session['cart'] = '{}'

        return order

    except Exception as e:
        raise Exception(_('Failed to create order'))


def checkout_success(request):
    """
    View to handle successful checkout.
    """
    try:
        if not request.session.get('from_checkout', False):
            return redirect('base')

        payment_method = request.GET.get('payment_method', 'Unknown')
        order = create_order(request, payment_method, 'Paid')

        # Clear session data
        for key in ['from_checkout', 'from_cart', 'cart', 'total_price', 'promo_discount', 'total']:
            request.session.pop(key, None)

        messages.success(request, _('Thank you for your order!'))
        return render(request, 'checkout_success.html', {'order': order})

    except Exception as e:
        messages.error(request, _(
            'An error occurred while processing your order.'))
        return redirect('cart')


def checkout_cancel(request):
    """
    View to handle cancelled checkout.
    """
    messages.warning(request, _('Your checkout was cancelled.'))
    return redirect('cart')
