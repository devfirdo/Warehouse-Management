# Generated by Django 5.0 on 2024-01-18 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WarehouseManagement', '0006_orderitem'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OrderItem',
        ),
    ]