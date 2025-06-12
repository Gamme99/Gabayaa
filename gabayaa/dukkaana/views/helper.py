from decimal import ROUND_HALF_UP, Decimal
import json

from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from ..models import CartItem
from ..constants import TRANSACTION_FEE_PERCENTAGE


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


def get_cart_totals(cart_items, include_fee=True):
    """
    Helper function to calculate cart totals.
    """
    try:
        # Handle both CartItem objects and dictionary cart items
        if cart_items and isinstance(next(iter(cart_items)), CartItem):
            # For CartItem objects (authenticated users)
            subtotal = sum(item.unit_price *
                           item.quantity for item in cart_items)
        else:
            # For dictionary cart items (guest users)
            subtotal = sum(
                Decimal(str(item['price'])) * item['quantity'] for item in cart_items)

        transaction_fee = subtotal * \
            TRANSACTION_FEE_PERCENTAGE if include_fee else Decimal('0')
        total = subtotal + transaction_fee

        return {
            'subtotal': round(subtotal, 2),
            'transaction_fee': round(transaction_fee, 2),
            'total': round(total, 2),
            'total_items': sum(item.quantity if hasattr(item, 'quantity') else item['quantity'] for item in cart_items)
        }
    except Exception as e:
        print(f"Error calculating cart totals: {str(e)}")
        return {
            'subtotal': Decimal('0'),
            'transaction_fee': Decimal('0'),
            'total': Decimal('0'),
            'total_items': 0
        }
