# Generated by Django 4.2.1 on 2023-08-28 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0006_alter_product_description_alter_product_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
