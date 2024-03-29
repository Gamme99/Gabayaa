# Generated by Django 4.2.1 on 2023-08-25 01:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0002_alter_cart_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='total_items',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cart',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dukkaana.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dukkaana.product')),
            ],
            options={
                'db_table': 'cart_item',
            },
        ),
    ]
