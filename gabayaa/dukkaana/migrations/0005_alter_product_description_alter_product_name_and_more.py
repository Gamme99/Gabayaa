# Generated by Django 4.2.1 on 2023-08-26 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0004_alter_cartitem_unit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.CharField(default='description', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(default='product', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.FloatField(default=10.0, null=True),
        ),
    ]