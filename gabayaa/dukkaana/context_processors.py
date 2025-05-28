from types import SimpleNamespace
from .models import Cart, CartItem, Product  # Adjust import based on your app
from .views.cart_views import get_session_cart  # Your custom session cart helper


def cart_context(request):
    """
    Context processor to make cart information available in all templates.
    Supports both authenticated and guest (session-based) users.
    """
    cart = None
    cart_items = []
    total_items = 0
    total_price = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(
                cart=cart).select_related('product')
            total_items = sum(item.quantity for item in cart_items)
            total_price = cart.total_price
        except Cart.DoesNotExist:
            pass
    else:
        session_cart = get_session_cart(request)
        for item_id, item_data in session_cart.items():
            try:
                product = Product.objects.get(id=item_id, is_active=True)
                quantity = item_data.get('quantity', 0)
                price = item_data.get('price', 0)
                cart_items.append(SimpleNamespace(
                    product=product,
                    quantity=quantity,
                    unit_price=price,
                    get_total_price=lambda: quantity * price
                ))
                total_items += quantity
                total_price += price * quantity
            except Product.DoesNotExist:
                continue
        cart = SimpleNamespace(
            total_price=round(total_price, 2),
            transaction_fee=round(total_price * 0.03, 2)
        )

    return {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
    }
