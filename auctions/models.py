from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default='buyer')  # buyer, seller, admin
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Item(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Auction(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    start_price = models.FloatField()
    current_price = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Auction for {self.item.name}"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.FloatField()
    bid_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} bid {self.bid_amount}"
