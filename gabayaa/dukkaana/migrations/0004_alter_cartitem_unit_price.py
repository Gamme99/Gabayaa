# Generated by Django 4.2.1 on 2023-08-25 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0003_cart_total_items_cart_total_price_cartitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
