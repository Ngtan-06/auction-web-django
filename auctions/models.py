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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'items'

    def __str__(self):
        return self.name

class Auction(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='auction')
    bid_increment = models.IntegerField(default=10) # Bước giá mặc định
    start_price = models.IntegerField()
    current_price = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='pending') # pending, active, ended
    current_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctions_winning')

    class Meta:
        db_table = 'auctions'

    def __str__(self):
        return f"Auction for {self.item.name}"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.IntegerField()
    bid_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bids'

class AuctionResult(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    final_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'auction_results'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)