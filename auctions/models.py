from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (('admin', 'Admin'), ('seller', 'Seller'), ('bidder', 'Bidder'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='bidder')
    class Meta:
        db_table = 'users'  # Tên bảng chính xác trong Supabase

class Item(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'items'

class Auction(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE)
    start_price = models.FloatField()
    current_price = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='active')
    class Meta:
        db_table = 'auctions'

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.FloatField()
    bid_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'bids'
