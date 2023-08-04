from django.contrib import admin
from .models import Shoe, Cloth, Electronic, ProductImage
# Register your models here.

admin.site.register(ProductImage)
# admin.site.register(Product)
admin.site.register(Shoe)
admin.site.register(Cloth)
admin.site.register(Electronic)
