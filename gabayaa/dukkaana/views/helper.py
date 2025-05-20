import json

from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


def superuser_required(view_func):
    decorated_view = user_passes_test(
        is_superuser, login_url=reverse_lazy('login'))(view_func)
    return decorated_view


def calculate_item_count(cart):
    item_count = 0
    for item_id, item in cart.items():
        quantity = item.get('quantity')
        item_count += quantity

    # print("total: ", item_count)
    return item_count


def convertToDict(cart_json):
    cart = {}
    if isinstance(cart_json, str):
        # print("isinstance")
        cart = json.loads(cart_json)
    else:
        # print("is not, its dictionary")
        cart = cart_json
    return cart
