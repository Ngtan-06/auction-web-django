import resend, os
from django.utils import timezone
from django.template.loader import render_to_string
from django.db import transaction
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from .models import Bid, Notification, AuctionResult, Auction
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
    if auction.status != 'active':
        return
    
    auction.status = 'ended'
    # 1. Tìm người đặt giá cao nhất
    highest_bid = auction.bids.order_by('-bid_amount', '-bid_time').first()
    
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
            message=f"Chúc mừng! Bạn đã thắng phiên đấu giá {auction.item.name} với giá {highest_bid.bid_amount:,.0f} VNĐ."
        )
        
        # Ghi nhận người thắng vào bảng Auction
        auction.current_bidder = highest_bid.user
        auction.current_price = highest_bid.bid_amount

    auction.save()

resend.api_key = os.getenv("RESEND_API_KEY") # Thêm biến này vào Render Environment

def process_pending_emails():
    pending_results = AuctionResult.objects.filter(email_sent=False).select_related('winner', 'auction__item')[:1]
    sent_count = 0
    
    for result in pending_results:
        winner = result.winner
        auction = result.auction
        
        if winner.email:
            try:
                # Gửi email qua HTTP API của Resend (siêu nhanh < 0.5s, không lo timeout)
                r = resend.Emails.send({
                    "from": "onboarding@resend.dev", # Tên người gửi mặc định
                    "to": winner.email,
                    "subject": f"🎉 Chúc mừng! Bạn đã thắng đấu giá: {auction.item.name}",
                    "html": f"""
                                <h2>Chúc mừng {winner.username}!</h2>
                                <p>Bạn đã chiến thắng cuộc đấu giá cho sản phẩm <strong>{auction.item.name}</strong>.</p>
                                <p>Giá chốt phiên: <strong>{auction.current_price} VND</strong>.</p>
                                <p>Vui lòng tiến hành thanh toán trong vòng 24 giờ để hoàn tất đơn hàng.</p>
                            """
                })
                
                result.email_sent = True
                result.save()
                sent_count += 1
                print(f"✅ Đã gửi email tới {winner.email}", flush=True)
            except Exception as e:
                print(f"❌ Lỗi gửi email cho {winner.email}: {e}", flush=True)
                
    return sent_count

def check_and_update_auctions():
    now = timezone.now()
    # 1. MỞ PHIÊN ĐẤU GIÁ (pending -> active)
    pending_auctions = Auction.objects.filter(status='pending', start_time__lte=now)
    
    # Sử dụng .update() để thay đổi hàng loạt trong 1 câu lệnh SQL duy nhất (Rất tối ưu)
    opened_count = pending_auctions.update(status='active')

    # 2. ĐÓNG PHIÊN ĐẤU GIÁ (active -> ended)
    closed_count = 0
    with transaction.atomic():
        ended_auctions = Auction.objects.select_for_update(skip_locked=True).filter(
            status='active', end_time__lte=now
        )
        for auction in ended_auctions:
            finalize_auction(auction)
            closed_count += 1
            
    return {
        "opened": opened_count,
        "closed": closed_count
    }