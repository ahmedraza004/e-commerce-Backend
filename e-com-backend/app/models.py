from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# models.py
# class User(AbstractUser):
#     name = models.CharField(max_length=20)
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    description = models.TextField()

    def __str__(self):
        return self.name
class Cart(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('checked_out', 'Checked Out'),
        ('abandoned', 'Abandoned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    items = models.ManyToManyField(Product, through='CartItem',related_name="cart_items")

    def __str__(self):
     return f"Cart #{self.id} - {self.status}"
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(max_length=26, choices=STATUS_CHOICES, default='pending')
    cart = models.ForeignKey(Cart,on_delete=models.SET_NULL,null=True,blank=True)
    item = models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username