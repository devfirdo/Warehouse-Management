from django.db import models
from django.contrib.auth.models import AbstractUser 

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=10,default=1)

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_stock = models.IntegerField(null=True)
    product_price = models.IntegerField(null=True)
    product_description = models.CharField(max_length=250, null=True)
    product_specification = models.CharField(max_length=250, null=True)
    product_image = models.ImageField(null=True, upload_to='images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class UserMember(models.Model):
    user_member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    number = models.IntegerField()
    image = models.ImageField(blank=True, upload_to='images/', null=True)
    address = models.TextField(blank=True, null=True)
    pancard = models.CharField(max_length=250, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Cart(models.Model):
    user_cart = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null = True)
    user_product = models.ForeignKey(Product, on_delete=models.CASCADE, null = True)
    quantity = models.PositiveIntegerField(default=1)
    def total_price(self):
        return self.quantity * self.user_product.product_price 





class ShippingMethod(models.Model):
    method_name = models.CharField(max_length=50)
    def __str__(self):
        return self.method_name

class Order(models.Model):
    TRACKING_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Dispatched', 'Dispatched'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField() 
    order_date = models.DateTimeField(auto_now_add=True)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    tracking_id = models.CharField(max_length=20, unique=True)
    delivery_date = models.DateField(null=True, blank=True) 
    tracking_status = models.CharField(
        max_length=20,
        choices=TRACKING_STATUS_CHOICES,
        default='Pending',
    )
    

class AssignedOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Dispatched', 'Dispatched'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='assigned_orders')
    delivery_guy = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)
    dispatched_location = models.CharField(max_length=100, blank=True, null=True)
    transit_location = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery_date = models.DateTimeField(null=True, blank=True)  
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
    )
    delivered_date = models.DateTimeField(null=True, blank=True)
    




