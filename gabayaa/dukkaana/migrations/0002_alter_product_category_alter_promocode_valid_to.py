# Generated by Django 4.2.1 on 2025-05-13 22:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('Huccuu', 'Huccuu'), ('Kophee', 'Kophee'), ('Electrooniksii', 'Electrooniksii'), ('Other', 'Other')], default='Other', max_length=20, verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 20, 22, 10, 23, 410523, tzinfo=datetime.timezone.utc), verbose_name='valid to'),
        ),
    ]
