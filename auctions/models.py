from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (('admin', 'Admin'), ('seller', 'Seller'), ('bidder', 'Bidder'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='bidder')
    class Meta:
        db_table = 'users'

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.name

class Item(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    # Thêm trường category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'items'

    def __str__(self):
        return self.name

class Auction(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='auction')
    bid_increment = models.DecimalField(max_digits=10, decimal_places=2, default=10.00) # Bước giá mặc định
    start_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='pending') # pending, active, ended

    class Meta:
        db_table = 'auctions'

    def __str__(self):
        return f"Auction for {self.item.name}"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bids'

# models.py
class AuctionResult(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    final_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auction_results'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)