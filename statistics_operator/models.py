from django.db import models
from django.contrib.auth.models import User
	

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)   
    phone_number = models.CharField(max_length=20, blank=False)   
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)   
    date_joined = models.DateTimeField()   

    def __str__(self):
        return f"Customer {self.username} (ID {self.customer_id})"


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    purchase_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchases')
    book_id = models.IntegerField()  
    book_title = models.CharField(max_length=255)   
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    purchase_date = models.DateTimeField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f"Purchase {self.purchase_id} by {self.customer.username}"

    class Meta:
        ordering = ['-purchase_date'] 