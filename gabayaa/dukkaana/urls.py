from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.base, name='base'),
    path('shoes', views.shoes, name='shoes'),
    path('cloths', views.cloths, name='cloths'),
    path('electronics', views.electronics, name='electronics'),
    path('renting', views.renting, name='renting'),
    path('buying', views.buying, name='buying'),
    path('product_info/<str:category>/<str:id>/',
         views.product_info, name='product_info'),

    path('cart', views.cart, name='cart'),
    path('add_to_cart<str:category>/<str:id>/',
         views.add_to_cart, name='add_to_cart'),
    path('remove_cart_item<str:id>/',
         views.remove_cart_item, name='remove_cart_item'),
    path('decrease_quantity<str:id>',
         views.decrease_quantity, name='decrease_quantity'),
    path('increase_quantity<str:id>',
         views.increase_quantity, name='increase_quantity'),
    path('edit_quantity<str:id>',
         views.edit_quantity, name='edit_quantity'),


    path('checkout', views.checkout, name='checkout'),
    path('checkout/success', views.checkout_success, name='success'),
    path('checkout/cancel', views.checkout_cancel, name='cancel'),

    path('manager/add_shoe', views.add_shoe, name='add_shoe'),
    path('manager/add_cloth', views.add_cloth, name='add_cloth'),
    path('manager/add_electronic', views.add_electronic, name='add_electronic'),
    path('manager/view_products', views.view_products, name='view_products'),
    path('search/', views.search_products, name='search_products'),
    path('manager', views.manager, name='manager'),
    path('login', views.loginManager, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logoutManager, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
