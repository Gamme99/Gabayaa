from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST, require_http_methods
from django.core.mail import send_mail
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
import uuid
import stripe
import requests
from decimal import ROUND_HALF_UP, Decimal
from ..models import CartItem, Order, OrderItem, PromoCode, Product, Cart, Customer
from ..utils.cart import CartSummary
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
import logging

from .helper import get_cart_totals
from .cart_views import get_session_cart
from ..constants import TRANSACTION_FEE_PERCENTAGE
from ..forms import CheckoutForm
from paypal.standard.ipn import views as paypal_ipn_views

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


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
            price = Decimal(str(item['price']))
            name = item['name']
            quantity = item['quantity']

        if promo_discount:
            price = price * (1 - Decimal(promo_discount))

        # Add transaction fee
        # price = price * Decimal('1.03')
        print(f"cart_items------: {cart_items}")

        totals = get_cart_totals(cart_items, include_fee=False)
        # print("✅ after total", flush=True)

        # price_cent = int(round(totals['total'] * 100))  # Convert to cents
        price_cent = int(round(price * 100))  # Convert to cents

        print(f"totals: {totals}")
        print(f"price cnet: {price_cent}")

        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': price_cent,
                'product_data': {
                    'name': name,
                },
            },
            'quantity': quantity,
        })

    transaction_fee = (totals['subtotal'] * TRANSACTION_FEE_PERCENTAGE).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP)

    if transaction_fee > 0:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int((transaction_fee * 100).to_integral_value(ROUND_HALF_UP)),
                'product_data': {
                    'name': 'Transaction Fee',
                },
            },
            'quantity': 1,
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
        request.session['from_cart'] = False
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

        # Store payment method in session
        request.session['payment_method'] = 'Stripe'

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
        print(f"Error in stripe_checkout: {str(e)}")
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
        # Get cart and calculate totals
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
            item_details = [{
                'name': item.product.name,
                'price': str(item.unit_price),
                'quantity': item.quantity,
            } for item in cart_items]
            subtotal = sum(item.unit_price *
                           item.quantity for item in cart_items)
            item_total = sum(item.quantity for item in cart_items)
        else:
            cart = get_session_cart(request)
            item_details = [{
                'name': item['name'],
                'price': str(item['price']),
                'quantity': item['quantity'],
            } for item in cart.values()]
            subtotal = sum(
                Decimal(str(item['price'])) * item['quantity'] for item in cart.values())
            item_total = sum(item['quantity'] for item in cart.values())

        # Apply promo discount if exists
        promo_discount = request.session.get('promo_discount', '0.00')
        if promo_discount:
            subtotal = subtotal * (1 - Decimal(promo_discount))

        # Add transaction fee
        transaction_fee = subtotal * Decimal('0.03')
        total_price = subtotal + transaction_fee

        # Generate a unique invoice ID
        invoice_id = str(uuid.uuid4())

        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': str(total_price),
            'item_name': 'Order',
            'invoice': invoice_id,
            'currency_code': 'USD',
            'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
            'return_url': request.build_absolute_uri(reverse('checkout_success')),
            'cancel_url': request.build_absolute_uri(reverse('checkout_cancel')),
            'item_total': item_total,
            'items': item_details,
            'custom': str(request.user.id) if request.user.is_authenticated else 'guest',
        }

        # Store only essential data in session
        request.session['paypal_invoice_id'] = invoice_id
        request.session['payment_method'] = 'PayPal'

        form = PayPalPaymentsForm(initial=paypal_dict)

        context = {
            "form": form,
            "cart": cart,
            "total_price": total_price,
            "transaction_fee": transaction_fee,
            "subtotal": subtotal,
            'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID
        }
        return render(request, 'checkout/paypal_checkout.html', context)

    except Exception as e:
        logger.error(f"Error in PayPal checkout: {str(e)}")
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


@require_POST
def process_checkout(request):
    try:
        # Get cart items based on user authentication
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
            if not cart_items.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Your cart is empty'
                })
        else:
            cart = get_session_cart(request)
            if not cart:
                return JsonResponse({
                    'success': False,
                    'error': 'Your cart is empty'
                })

        # Get shipping information from the form
        shipping_data = {
            'email': request.POST.get('email'),
            'full_name': request.POST.get('full_name'),
            'address': request.POST.get('address'),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'zip_code': request.POST.get('zip_code'),
            'phone': request.POST.get('phone')
        }

        # Store shipping information in session
        request.session['shipping_info'] = shipping_data
        request.session['from_cart'] = True

        # Get payment method
        payment_method = request.POST.get('payment_method')

        # Calculate totals
        if request.user.is_authenticated:
            subtotal = sum(item.unit_price *
                           item.quantity for item in cart_items)
        else:
            subtotal = sum(
                Decimal(str(item['price'])) * item['quantity'] for item in cart.values())

        transaction_fee = subtotal * Decimal('0.03')  # 3% transaction fee
        total = subtotal + transaction_fee

        # Store payment info in session
        request.session['payment_info'] = {
            'subtotal': str(subtotal),
            'transaction_fee': str(transaction_fee),
            'total': str(total),
            'payment_method': payment_method
        }

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('stripe_checkout' if payment_method == 'stripe' else 'paypal_checkout')
        })

    except Exception as e:
        logger.error(f"Error processing checkout: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your checkout'
        })


def payment_method(request):
    """
    View to select payment method after shipping information is collected.
    """
    if not request.session.get('shipping_info'):
        messages.warning(request, _(
            'Please provide shipping information first.'))
        return redirect('checkout')

    return render(request, 'checkout/payment_method.html')


def create_order(request, payment_method, payment_status='Pending'):
    """
    Helper function to create an order with shipping information.
    """
    try:
        shipping_info = request.session.get('shipping_info', {})
        if not shipping_info:
            raise Exception(_('Shipping information is required'))

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
            subtotal = sum(item.unit_price *
                           item.quantity for item in cart_items)
            transaction_fee = subtotal * Decimal('0.03')
            total_price = subtotal + transaction_fee
            user = request.user
        else:
            cart = get_session_cart(request)
            cart_items = cart.values()
            subtotal = sum(
                Decimal(str(item['price'])) * item['quantity'] for item in cart_items)
            transaction_fee = subtotal * Decimal('0.03')
            total_price = subtotal + transaction_fee

            # Create or get guest customer
            guest_user, created = Customer.objects.get_or_create(
                email=shipping_info['email'],
                defaults={
                    'username': shipping_info['email'],
                    'first_name': shipping_info['full_name'].split()[0],
                    'last_name': ' '.join(shipping_info['full_name'].split()[1:]),
                    'is_active': False
                }
            )
            user = guest_user

        # Create shipping address string
        shipping_address = f"{shipping_info['address']}, {shipping_info['city']}, {shipping_info['state']}, {shipping_info['zip_code']}"

        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_price,
            shipping_address=shipping_address,
            email=shipping_info['email'],
            phone=shipping_info['phone'],
            payment_method=payment_method,
            payment_status=payment_status,
            status='Pending',
            transaction_fee=transaction_fee
        )

        # Create order items
        for item in cart_items:
            if isinstance(item, CartItem):
                product = item.product
                quantity = item.quantity
                price = item.unit_price
            else:
                product = get_object_or_404(Product, id=item['id'])
                quantity = item['quantity']
                price = Decimal(str(item['price']))

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=quantity,
                price=price
            )

        # Clear cart
        if request.user.is_authenticated:
            cart.delete()
        else:
            request.session['cart'] = '{}'

        # Send order confirmation email
        send_mail(
            _('Order Confirmation - Gabayaa'),
            _('Thank you for your order! Your order has been received and is being processed.'),
            settings.DEFAULT_FROM_EMAIL,
            [shipping_info['email']],
            fail_silently=True,
        )

        return order

    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise Exception(_('Failed to create order'))


def checkout_success(request):
    """
    View to handle successful checkout.
    """
    try:
        # Check if this is a PayPal redirect
        payer_id = request.GET.get('PayerID')
        payment_method = 'PayPal' if payer_id else request.session.get(
            'payment_method', 'Stripe')
        payment_status = 'Paid'

        # Create the order
        order = create_order(request, payment_method, payment_status)

        # Get customer name
        if order.user.is_authenticated:
            customer_name = order.user.get_full_name() or order.user.username
        else:
            # For guest users, use the full name from shipping info
            shipping_info = request.session.get('shipping_info', {})
            customer_name = shipping_info.get('full_name', order.email)

        # Clear only essential session data
        for key in ['cart', 'payment_method', 'shipping_info', 'paypal_invoice_id']:
            request.session.pop(key, None)

        messages.success(request, _('Thank you for your order!'))
        return render(request, 'checkout/success.html', {
            'order': order,
            'email': order.email,
            'customer': customer_name
        })

    except Exception as e:
        logger.error(f"Error in checkout_success: {str(e)}")
        messages.error(request, _(
            'An error occurred while processing your order.'))
        return redirect('cart')


def checkout_cancel(request):
    """
    View to handle cancelled checkout.
    """
    messages.warning(request, _('Your checkout was cancelled.'))
    return redirect('cart')
