from django.urls import path, include

from .views import authenticate_views
from . import views
from .views import authenticate_views, product_views, manager_views, cart_views, payment_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', product_views.home, name='home'),
    path('manager', authenticate_views.manager, name='manager'),
    path('login', authenticate_views.login_view, name='login'),
    path('customer/register', authenticate_views.register_view,
         name='register'),
    path('customer/update_customer/<str:id>',
         authenticate_views.update_user, name='update_user'),
    path('customer/logout', authenticate_views.logout_view,
         name='logout_customer'),
    path('logout', authenticate_views.logout_view, name='logout'),
    path('password_reset', authenticate_views.password_reset,
         name='password_reset'),

    path('huccuu', product_views.cloths, name='cloths'),
    path('kophee', product_views.shoes, name='shoes'),
    path('elektrooniksii', product_views.electronics, name='electronics'),
    path('product_info/<str:category>/<str:id>/',
         product_views.product_info, name='product_info'),
    path('search', product_views.search_results, name='search_results'),
    path('add_review/<str:product_id>/',
         product_views.add_review, name='add_review'),
    path('cart', cart_views.view_cart, name='cart'),
    path('add_to_cart/<uuid:product_id>/',
         cart_views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/',
         cart_views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/',
         cart_views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', cart_views.clear_cart, name='clear_cart'),
    path('get_promo', cart_views.get_promo, name='get_promo'),
    path('update_total_after_discount', cart_views.update_total_after_discount,
         name='update_total_after_discount'),

    path('stripe_checkout', payment_views.stripe_checkout, name='stripe_checkout'),
    path('paypal_checkout', payment_views.paypal_checkout, name='paypal_checkout'),
    path('checkout/success', payment_views.checkout_success, name='success'),
    path('checkout/cancel', payment_views.checkout_cancel, name='cancel'),
    path('paypal/', include('paypal.standard.ipn.urls')),

    #     path('manager', authenticate_views.manager, name='manager'),
    path('manager/add_product', manager_views.add_product, name='add_product'),
    path('manager/view_products', manager_views.view_products, name='view_products'),
    path('manager/view_product/search',
         manager_views.search_products, name='search_products'),
    path('manager/customer_list', manager_views.customer_list, name='customer_list'),
    path('manager/customer_search',
         manager_views.customer_search, name='customer_search'),
    path('manager/order_list', manager_views.order_list, name='order_list'),
    path('manager/order_list/order_search',
         manager_views.order_search, name='order_search'),
    path('manager/order_list/update_status',
         manager_views.update_status, name='update_status'),
    path('manager/edit_product/<str:id>',
         manager_views.edit_product, name='edit_product'),
    path('manager/delete_product/<str:id>',
         manager_views.delete_product, name='delete_product'),
    path('manager/create_promo_code',
         manager_views.create_promo_code, name='create_promo_code'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
