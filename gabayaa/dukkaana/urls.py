from django.urls import path, include

from .views import authenticate_views, product_views, manager_views, cart_views, payment_views, order_views, review_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from paypal.standard.ipn import views as paypal_ipn_views

urlpatterns = [
    # Home and Authentication URLs
    path('', product_views.home, name='home'),
    path('login', authenticate_views.login_view, name='login'),
    path('logout', authenticate_views.logout_view, name='logout'),
    path('password_reset', authenticate_views.password_reset, name='password_reset'),

    # Customer URLs
    #     path('user/register', authenticate_views.register_view, name='register'),
    path('user/update_user/<str:id>',
         authenticate_views.update_user, name='update_user'),
    path('user/logout', authenticate_views.logout_view, name='logout_customer'),

    # Product URLs
    path('huccuu', product_views.cloths, name='cloths'),
    path('kophee', product_views.shoes, name='shoes'),
    path('elektrooniksii', product_views.electronics, name='electronics'),
    path('product/<uuid:id>/', product_views.product_detail, name='product_detail'),
    path('search', product_views.search_results, name='search_results'),
    path('add_review/<str:product_id>/',
         product_views.add_review, name='add_review'),

    # Cart URLs
    path('cart', cart_views.view_cart, name='cart'),
    path('cart/add/<uuid:product_id>/',
         cart_views.add_to_cart, name='add_to_cart'),
    path('cart/update/<uuid:item_id>/',
         cart_views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<uuid:item_id>/',
         cart_views.remove_cart_item, name='remove_cart_item'),
    path('cart/clear/', cart_views.clear_cart, name='clear_cart'),
    path('cart/apply-promo/', cart_views.apply_promo_code, name='apply_promo_code'),

    # Payment URLs
    path('checkout/process/', payment_views.process_checkout,
         name='process_checkout'),
    path('checkout/stripe/', payment_views.stripe_checkout, name='stripe_checkout'),
    path('checkout/paypal/', payment_views.paypal_checkout, name='paypal_checkout'),
    path('checkout/success/', payment_views.checkout_success,
         name='checkout_success'),
    path('checkout/cancel/', payment_views.checkout_cancel, name='checkout_cancel'),
    path('paypal-ipn/', paypal_ipn_views.ipn, name='paypal-ipn'),

    # Order URLs
    path('orders/', order_views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', order_views.order_detail, name='order_detail'),
    #     path('orders/<uuid:order_id>/cancel/',
    #          order_views.cancel_order, name='cancel_order'),
    #     path('orders/<uuid:order_id>/track/',
    #          order_views.track_order, name='track_order'),

    # Manager URLs
    path('manager', authenticate_views.manager, name='manager'),
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
    path('manager/register/', manager_views.register_customer, name='register'),
    path('manager/customers/', manager_views.customer_list, name='customer_list'),
    path('manager/customers/<int:customer_id>/orders/',
         manager_views.customer_orders, name='customer_orders'),
    path('manager/customers/<int:customer_id>/edit/',
         manager_views.edit_customer, name='edit_customer'),
    path('manager/customers/<int:customer_id>/delete/',
         manager_views.delete_customer, name='delete_customer'),

    # Review URLs
    path('review/<int:review_id>/delete/',
         review_views.delete_review, name='delete_review'),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
