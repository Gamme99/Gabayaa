# Generated by Django 4.2.1 on 2023-05-16 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cloth',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='electronic',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='shoe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
