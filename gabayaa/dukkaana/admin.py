# from django.contrib import admin
# from .models import Product, Shoe, Cloth, Electronic, ProductImage


# # class ProductImageInline(admin.TabularInline):
# #     model = ProductImage


# # class ProductAdmin(admin.ModelAdmin):
# #     inlines = [ProductImageInline]


# # admin.site.register(Product, ProductAdmin)
# admin.site.register(Shoe)
# admin.site.register(Cloth)
# admin.site.register(Electronic)


from django.contrib import admin
from .models import Shoe, Cloth, Electronic
# Register your models here.

# admin.site.register(Product)
admin.site.register(Shoe)
admin.site.register(Cloth)
admin.site.register(Electronic)
