from .models import Cart, CartItem


def cart_context(request):
    """
    Context processor to make cart information available in all templates.
    """
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            total_items = sum(item.quantity for item in cart_items)
            total_price = cart.total_price
        except Cart.DoesNotExist:
            cart = None
            cart_items = []
            total_items = 0
            total_price = 0
    else:
        cart = None
        cart_items = []
        total_items = 0
        total_price = 0

    return {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
    }
