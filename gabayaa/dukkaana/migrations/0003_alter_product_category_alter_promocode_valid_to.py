# Generated by Django 4.2.1 on 2025-05-13 22:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0002_alter_product_category_alter_promocode_valid_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('Huccuu', 'Huccuu'), ('Kophee', 'Kophee'), ('Electrooniksii', 'Electrooniksii')], default='Huccuu', max_length=20, verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 20, 22, 31, 42, 580728, tzinfo=datetime.timezone.utc), verbose_name='valid to'),
        ),
    ]
