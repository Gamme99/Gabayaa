from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from ..models import Order, OrderItem


@login_required
def order_list(request):
    """
    View to display a list of user's orders.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })


@login_required
def order_detail(request, order_id):
    """
    View to display details of a specific order.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(
        order=order).select_related('product')

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'order_items': order_items
    })
