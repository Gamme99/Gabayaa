from django.urls import path, include
from . import views
from .views import authenticate_views, product_views, manager_views, cart_views, payment_views, authenticate_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', authenticate_views.base, name='base'),
    path('manager', authenticate_views.manager, name='manager'),
    path('login', authenticate_views.loginManager, name='login'),
    path('register', authenticate_views.register, name='register'),
    path('customer/register', authenticate_views.register_customer,
         name='register_customer'),
    path('customer/login', authenticate_views.login_customer, name='login_customer'),
    path('logout', authenticate_views.logoutManager, name='logout'),

    path('shoes', product_views.shoes, name='shoes'),
    path('cloths', product_views.cloths, name='cloths'),
    path('electronics', product_views.electronics, name='electronics'),
    path('renting', product_views.renting, name='renting'),
    path('buying', product_views.buying, name='buying'),
    path('product_info/<str:category>/<str:id>/',
         product_views.product_info, name='product_info'),

    path('cart', cart_views.cart, name='cart'),
    #     path('mycart', cart_views.cart, name='mycart'),
    path('add_to_cart<str:category>/<str:id>/',
         cart_views.add_to_cart, name='add_to_cart'),
    path('remove_cart_item<str:id>/',
         cart_views.remove_cart_item, name='remove_cart_item'),
    path('decrease_quantity<str:id>',
         cart_views.decrease_quantity, name='decrease_quantity'),
    path('increase_quantity<str:id>',
         cart_views.increase_quantity, name='increase_quantity'),
    path('edit_quantity<str:id>',
         cart_views.edit_quantity, name='edit_quantity'),


    path('checkout', payment_views.stripeCheckout, name='checkout'),
    path('paypal_checkout', payment_views.paypal_checkout, name='paypal_checkout'),
    path('checkout/success', payment_views.checkout_success, name='success'),
    path('checkout/cancel', payment_views.checkout_cancel, name='cancel'),
    path('paypal/', include('paypal.standard.ipn.urls')),

    path('manager/add_product', manager_views.add_product, name='add_product'),
    path('manager/view_products', manager_views.view_products, name='view_products'),
    path('search/', manager_views.search_products, name='search_products'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
