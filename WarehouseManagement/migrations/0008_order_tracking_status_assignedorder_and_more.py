# Generated by Django 5.0 on 2024-01-18 11:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WarehouseManagement', '0007_delete_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tracking_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='AssignedOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
                ('dispatched_location', models.CharField(blank=True, max_length=100, null=True)),
                ('in_transit_location', models.CharField(blank=True, max_length=100, null=True)),
                ('delivered_location', models.CharField(blank=True, max_length=100, null=True)),
                ('is_delivered', models.BooleanField(default=False)),
                ('delivery_guy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WarehouseManagement.order')),
            ],
        ),
        migrations.DeleteModel(
            name='OrderAssignment',
        ),
    ]
