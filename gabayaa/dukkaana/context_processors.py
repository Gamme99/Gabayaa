from decimal import Decimal
from types import SimpleNamespace

from .models import Cart, CartItem, Product  # Adjust import based on your app
from .views.cart_views import get_session_cart  # Your custom session cart helper
from .utils.cart import CartSummary  # Import CartSummary from utils


def cart_context(request):
    """
    Context processor to make cart information available in all templates.
    Supports both authenticated and guest (session-based) users.
    """
    cart = None
    cart_items = []

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
        except Cart.DoesNotExist:
            pass
    else:
        session_cart = get_session_cart(request)
        for item_id, item_data in session_cart.items():
            try:
                product = Product.objects.get(id=item_id, is_active=True)
                cart_items.append({
                    'product': product,
                    'quantity': item_data.get('quantity', 0),
                    'price': item_data.get('price', 0),
                })
            except Product.DoesNotExist:
                continue

    # Calculate cart summary
    summary = CartSummary(cart_items)

    return {
        'cart': cart,
        'cart_items': cart_items,
        'cart_summary': summary.to_dict()
    }
