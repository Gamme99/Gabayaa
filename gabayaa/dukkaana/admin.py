from django.contrib import admin
# from .models import Shoe, Cloth, Electronic, ProductImage, Customer, Product
from .models import ProductImage, Customer, Product, Cart, CartItem
# from .user_model import Customer
# Register your models here.

admin.site.register(Product)
admin.site.register(ProductImage)
# admin.site.register(Shoe)
# admin.site.register(Cloth)
# admin.site.register(Electronic)
admin.site.register(Cart)
admin.site.register(CartItem)

admin.site.register(Customer)
