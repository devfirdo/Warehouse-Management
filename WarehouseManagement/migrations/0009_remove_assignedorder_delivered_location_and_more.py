# Generated by Django 5.0 on 2024-01-18 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WarehouseManagement', '0008_order_tracking_status_assignedorder_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignedorder',
            name='delivered_location',
        ),
        migrations.RemoveField(
            model_name='assignedorder',
            name='dispatched_location',
        ),
        migrations.RemoveField(
            model_name='assignedorder',
            name='in_transit_location',
        ),
        migrations.RemoveField(
            model_name='order',
            name='is_delivered',
        ),
        migrations.AddField(
            model_name='assignedorder',
            name='location',
            field=models.CharField(blank=True, choices=[('Dispatched', 'Dispatched'), ('In Transit', 'In Transit'), ('Delivered', 'Delivered')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='tracking_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Dispatched', 'Dispatched'), ('In Transit', 'In Transit'), ('Delivered', 'Delivered')], default='Pending', max_length=20),
        ),
    ]