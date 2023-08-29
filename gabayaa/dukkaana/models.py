from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager

from django.contrib.auth import get_user_model


class MyAccountManager(BaseUserManager):

    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email address.")
        if not username:
            raise ValueError("Users must have an username.")
        user = self.model(email=self.normalize_email(
            email), username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        # user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Customer(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True)
    street_address = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=20, null=True)
    state = models.CharField(max_length=20, null=True)
    zip_code = models.CharField(max_length=10, null=True)
    billing_address = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyAccountManager()

    def __str__(self):
        return self.username


class Product(models.Model):
    CATEGORY = (
        ('Shoe', 'Shoe'),
        ('Cloth', 'Cloth'),
        ('Electronic', 'Electronic'),
    )
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    description = models.CharField(max_length=200, null=True)
    image = models.CharField(max_length=200, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new instance, not an update
            unique_id = get_random_string(length=8, allowed_chars='0123456789')
            self.pk = unique_id

        super().save(*args, **kwargs)

    def get_first_image_from_files(self):
        images = self.product_images.all()
        if images.exists():
            return images.first().image
        return None

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    image = models.ImageField(upload_to='images/')
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_image'

    def __str__(self):
        return f"Image for {self.productId.name}"


class Cart(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_items = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'cart'

    def __str__(self):
        return f"{self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    unit_price = models.DecimalField(
        default=0.00, max_digits=10, decimal_places=2)  # Price of one item

    def get_total_price(self):
        return self.unit_price * self.quantity

    class Meta:
        db_table = 'cart_item'

    def __str__(self):
        return f"{self.product} for {self.cart}"


class Order(models.Model):
    # user = models.CharField(get_user_model(), on_delete=models.CASCADE, null=True)
    # CharField to store user information
    user = models.CharField(max_length=255)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=(
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ), default='Pending')

    def __str__(self):
        return f"Order {self.pk} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} for ({self.order.user})"
