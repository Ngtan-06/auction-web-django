from django.contrib.auth.hashers import make_password
from decimal import Decimal
from .models import Bid, Notification, AuctionResult
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def calculate_next_bid(auction):
    # Giá tiếp theo = Giá hiện tại + Bước giá
    return auction.current_price + auction.bid_increment

def place_bid(user, auction):
    next_bid = auction.current_price + auction.bid_increment
    # ... lưu Bid ...
    auction.current_price = next_bid
    auction.save()
    next_price = next_bid + auction.bid_increment
    # Kích hoạt WebSocket gửi giá mới cho mọi người
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'auction_{auction.id}',
        {'type': 'send_new_bid',
         'current_price': str(next_bid),
         'next_bid': str(next_price)}
    )

def finalize_auction(auction):
    # 1. Tìm người đặt giá cao nhất
    highest_bid = auction.bids.order_by('-bid_amount').first()
    
    if highest_bid:
        # 2. Lưu kết quả
        AuctionResult.objects.create(
            auction=auction,
            winner=highest_bid.user,
            final_price=highest_bid.bid_amount
        )
        
        # 3. Tạo thông báo cho người thắng
        Notification.objects.create(
            user=highest_bid.user,
            message=f"Chúc mừng! Bạn đã thắng phiên đấu giá {auction.item.name} với giá {highest_bid.bid_amount}."
        )
    
    auction.status = 'ended'
    auction.save()