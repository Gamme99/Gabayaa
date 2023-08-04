from django.shortcuts import render, redirect
from django.urls import reverse
from .helper import calculate_item_count, convertToDict
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
import uuid
import stripe
import requests

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    YOUR_DOMAIN = 'http://127.0.0.1:8000/checkout'
    cart_json = request.session.get('cart', {})
    cart = convertToDict(cart_json)
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


def get_access_token(client_id, client_secret):
    url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, headers=headers,
                             data=data, auth=(client_id, client_secret))

    response.raise_for_status()
    print("________________________")
    print(client_id)
    print(client_secret)
    print(response)
    print(response.json()['access_token'])
    print("________________________")
    return response.json()['access_token']

# @login_required("cart")


def paypal_checkout(request):

    host = request.get_host()
    totala_price = request.session['total_price']
    print("host:", host)
    # Get the cart items from the session
    cart_json = request.session.get('cart', {})
    cart = convertToDict(cart_json)

    item_details = []
    for item_id, item in cart.items():
        item_name = item['name']
        item_price = item['price']
        item_quantity = item['quantity']

        # Create a dictionary for each item's details
        item_details.append({
            'name': item_name,
            'price': '{:.2f}'.format(item_price),
            'quantity': item_quantity,
        })
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': request.session['total_price'],
        'item_name': 'Order000',
        'invoice': str(uuid.uuid4()),
        'currency_code': 'USD',
        'notify_url': f'http://{host}{reverse("paypal-ipn")}',
        'return_url': f'http://{host}{reverse("success")}',
        'cancel_url': f'http://{host}{reverse("cancel")}',
        'item_total': calculate_item_count(cart),
        'items': item_details,
    }

    # print("item details: ", item_details)

    form = PayPalPaymentsForm(initial=paypal_dict)

    context = {"form": form, "cart": cart, "total_price": totala_price,
               'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID}

    # print("form---------: ", form)

    return render(request, 'paypal_checkout.html', context)


def paypal_return(request):
    return redirect('base')


def checkout_success(request):
    request.session['cart'] = {}
    return render(request, 'success.html')


def checkout_cancel(request):
    return render(request, 'cancel.html')
