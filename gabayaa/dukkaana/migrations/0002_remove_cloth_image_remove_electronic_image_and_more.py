# Generated by Django 4.2.1 on 2023-07-27 08:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cloth',
            name='image',
        ),
        migrations.RemoveField(
            model_name='electronic',
            name='image',
        ),
        migrations.RemoveField(
            model_name='shoe',
            name='image',
        ),
    ]
