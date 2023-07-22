from django.db import models


class Product(models.Model):
    CATEGORY = (
        ('Shoe', 'Shoe'),
        ('Cloth', 'Cloth'),
        ('Electronic', 'Electronic'),
    )
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @property
    def custom_id(self):
        return f"{self.category}_{self.pk}"

    id = custom_id


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
