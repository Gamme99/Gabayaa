from django.contrib import admin
# from .models import Shoe, Cloth, Electronic, ProductImage, Customer, Product
from .models import ProductImage, Customer, Product, Cart, CartItem, Order, OrderItem, PromoCode, Review
# from .user_model import Customer
# Register your models here.

# Custom Product admin to show id (UUID) in list and detail views


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_active')
    readonly_fields = ('id',)


admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(PromoCode)

admin.site.register(Customer)
admin.site.register(Review)
