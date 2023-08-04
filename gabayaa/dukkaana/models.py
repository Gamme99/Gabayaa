from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.crypto import get_random_string


class Product(models.Model):
    CATEGORY = (
        ('Shoe', 'Shoe'),
        ('Cloth', 'Cloth'),
        ('Electronic', 'Electronic'),
    )
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=True)
    description = models.CharField(max_length=200, null=True)
    image = models.CharField(max_length=200, null=True, blank=True)
    # image = models.ImageField(upload_to='images/', null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True
        # db_table = 'product'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new instance, not an update
            # Generate a unique ID based on category and random string
            unique_id = get_random_string(length=8, allowed_chars='0123456789')
            self.pk = unique_id

            # Set the first image from associated images as the "image" field
            # if not self.image:
            #     first_image = self.get_first_image_from_files()
            #     if first_image:
            #         self.image = first_image

        super().save(*args, **kwargs)

    def get_first_image_from_files(self):
        # Assuming you have a related_name in the ProductImage model
        images = self.product_images.all()
        if images.exists():
            return images.first().image
        return None


class ProductImage(models.Model):
    image = models.ImageField(upload_to='images/')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # Store the custom ID as a CharField
    object_id = models.CharField(max_length=200)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'product_image'

    # def save(self, *args, **kwargs):
    #     if not self.pk:  # Check if it's a new instance, not an update
    #         # Generate a unique ID based on content type and custom ID of the associated object
    #         self.object_id = f"{self.content_type.model}_{self.content_object.pk}"
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.object_id


class Shoe(Product):
    TYPE = (
        ('Outdoor', 'Outdoor'),
        ('Indoor', 'Indoor'),
        ('Man', 'Man'),
        ('Woman', 'Woman'),
        ('Kids', 'Kids'),
    )
    SIZE = (
        ('US 5', 'US 5'),
        ('US 6', 'US 6'),
        ('US 7', 'US 7'),
        ('US 9', 'US 9'),
        ('US 10', 'US 10'),
        ('US 11', 'US 11'),
        ('US 12', 'US 12'),
        ('US 13', 'US 13'),
    )

    type = models.CharField(max_length=200, null=True, choices=TYPE)
    size = models.CharField(max_length=200, null=True, choices=SIZE)

    class Meta:
        db_table = 'shoe'


class Cloth(Product):
    class Meta:
        db_table = 'cloth'

    def __str__(self):
        return self.name


class Electronic(Product):
    class Meta:
        db_table = 'electronic'

    def __str__(self):
        return self.name
