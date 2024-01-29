# Generated by Django 5.0 on 2024-01-17 17:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WarehouseManagement', '0002_product_usermember'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('user_cart', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='WarehouseManagement.product')),
            ],
        ),
    ]