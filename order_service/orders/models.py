from django.db import models
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('FAILED', 'Failed'),
    )

    user_id = models.IntegerField(db_index=True)
    product_id = models.IntegerField(db_index=True)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

class Cart(models.Model):
    user_id = models.IntegerField(db_index=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Cart for User {self.user_id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField(db_index=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product_id')

    def __str__(self):
        return f"{self.quantity} x Product {self.product_id} in Cart {self.cart.id}"
