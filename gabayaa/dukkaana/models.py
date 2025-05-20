from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import uuid
from django.core.validators import FileExtensionValidator
from datetime import timedelta


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError(_("Users must have an email address."))
        if not username:
            raise ValueError(_("Users must have a username."))
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Customer(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_(
                "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        )]
    )
    street_address = models.CharField(
        _('street address'), max_length=100, null=True)
    city = models.CharField(_('city'), max_length=50, null=True)
    state = models.CharField(_('state'), max_length=50, null=True)
    zip_code = models.CharField(
        _('zip code'),
        max_length=10,
        null=True,
        validators=[RegexValidator(
            regex=r'^\d{5}(-\d{4})?$',
            message=_("Zip code must be in the format: '12345' or '12345-6789'.")
        )]
    )
    billing_address = models.CharField(
        _('billing address'), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    email_verified = models.BooleanField(_('email verified'), default=False)
    phone_verified = models.BooleanField(_('phone verified'), default=False)

    objects = MyAccountManager()

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('customer_profile', args=[str(self.id)])


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Huccuu', _('Huccuu')),
        ('Kophee', _('Kophee')),
        ('Electrooniksii', _('Electrooniksii')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='Huccuu'
    )
    name = models.CharField(_('name'), max_length=200, default='no name')
    slug = models.SlugField(_('slug'), max_length=200,
                            unique=True, default='no-name')
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        default=0.00
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    description = models.TextField(_('description'), blank=True)
    features = models.TextField(_('features'), blank=True)
    specifications = models.JSONField(
        _('specifications'), default=dict, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    rating = models.DecimalField(
        _('rating'),
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.PositiveIntegerField(_('review count'), default=0)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_info', args=[self.category, self.id])

    def get_first_image(self):
        return self.images.first() if self.images.exists() else None

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            self.rating = sum(
                review.rating for review in reviews) / reviews.count()
            self.review_count = reviews.count()
            self.save()


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name=_('product')
    )
    image = models.ImageField(
        _('image'),
        upload_to='products/%Y/%m/%d/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]
    )
    is_primary = models.BooleanField(_('primary image'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name=_('user')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    total_items = models.PositiveIntegerField(_('total items'), default=0)
    transaction_fee = models.DecimalField(
        _('transaction fee'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    total_price = models.DecimalField(
        _('total price'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    promo_code = models.ForeignKey(
        'PromoCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name=_('promo code')
    )

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ['-created_at']

    def __str__(self):
        return f"Cart for {self.user.username}"

    def update_totals(self):
        items = self.items.all()
        self.total_items = sum(item.quantity for item in items)
        self.total_price = sum(item.get_total_price() for item in items)
        if self.promo_code and self.promo_code.is_active:
            discount = self.total_price * (self.promo_code.discount / 100)
            self.total_price -= discount
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('cart')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('product')
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        _('unit price'),
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"

    def get_total_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
        self.cart.update_totals()


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', _('Pending')),
        ('Processing', _('Processing')),
        ('Shipped', _('Shipped')),
        ('Delivered', _('Delivered')),
        ('Cancelled', _('Cancelled')),
        ('Refunded', _('Refunded')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_('user')
    )
    order_date = models.DateTimeField(_('order date'), auto_now_add=True)
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2
    )
    shipping_address = models.TextField(_('shipping address'))
    discount_percent = models.DecimalField(
        _('discount percent'),
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True
    )
    transaction_fee = models.DecimalField(
        _('transaction fee'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    tracking_number = models.CharField(
        _('tracking number'),
        max_length=100,
        blank=True,
        null=True
    )
    payment_method = models.CharField(
        _('payment method'),
        max_length=50
    )
    payment_status = models.CharField(
        _('payment status'),
        max_length=50
    )
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['order_date']),
        ]

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def get_absolute_url(self):
        return reverse('order_detail', args=[str(self.id)])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('product')
    )
    product_name = models.CharField(_('product name'), max_length=255)
    quantity = models.PositiveIntegerField(_('quantity'))
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in {self.order}"

    def get_total_price(self):
        return self.price * self.quantity


class PromoCode(models.Model):
    code = models.CharField(
        _('code'),
        max_length=50,
        unique=True
    )
    discount = models.DecimalField(
        _('discount'),
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(_('active'), default=True)
    valid_from = models.DateTimeField(_('valid from'), default=timezone.now)
    valid_to = models.DateTimeField(
        _('valid to'), default=timezone.now() + timedelta(weeks=1))
    max_uses = models.PositiveIntegerField(
        _('max uses'), null=True, blank=True)
    used_count = models.PositiveIntegerField(_('used count'), default=0)
    min_order_value = models.DecimalField(
        _('min order value'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('promo code')
        verbose_name_plural = _('promo codes')
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def use(self):
        self.used_count += 1
        self.save()


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('product')
    )
    user = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('user')
    )
    rating = models.PositiveSmallIntegerField(
        _('rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(_('title'), max_length=200)
    comment = models.TextField(_('comment'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_verified = models.BooleanField(_('verified'), default=False)

    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()
