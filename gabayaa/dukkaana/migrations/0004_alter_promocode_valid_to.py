# Generated by Django 4.2.1 on 2025-05-13 22:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0003_alter_product_category_alter_promocode_valid_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 20, 22, 36, 42, 92210, tzinfo=datetime.timezone.utc), verbose_name='valid to'),
        ),
    ]
