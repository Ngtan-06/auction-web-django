from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from .models import Bid, Notification, AuctionResult
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def place_bid(user, auction):
    next_bid = auction.current_price + auction.bid_increment

    # 1. Lưu vào Database
    new_bid = Bid.objects.create(
        user=user,
        auction=auction,
        bid_amount=next_bid,
        bid_time=timezone.now()
    )
    
    # 2. Cập nhật Auction
    auction.current_price = next_bid
    auction.current_bidder = user
    auction.save()
    
    # 3. Render đoạn HTML cho dòng lịch sử mới
    # Tạo một file nhỏ tên là 'bid_item.html' hoặc render trực tiếp string
    bid_html = render_to_string('partials/bid_item.html', {'bid': new_bid})
    
    # 4. Gửi qua WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'auction_{auction.id}',
        {
            'type': 'send_new_bid',
            'current_price': str(next_bid),
            'next_bid': str(next_bid + auction.bid_increment),
            'bid_html': bid_html, # Gửi đoạn HTML mới
            'bidder_id': user.id # Gửi ID của người đặt giá
        }
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