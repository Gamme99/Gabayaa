# Generated by Django 4.2.1 on 2023-07-28 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dukkaana', '0003_alter_productimage_object_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='content_type',
        ),
        migrations.AddField(
            model_name='cloth',
            name='custom_id',
            field=models.CharField(default=24452, editable=False, max_length=20, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='electronic',
            name='custom_id',
            field=models.CharField(default=24, editable=False, max_length=20, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shoe',
            name='custom_id',
            field=models.CharField(default=542, editable=False, max_length=20, unique=True),
            preserve_default=False,
        ),
    ]
