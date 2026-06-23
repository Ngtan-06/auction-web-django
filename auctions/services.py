from .supabase_client import supabase
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from .models import Bid, Notification, AuctionResult

# Lấy danh sách sản phẩm từ bảng items
def get_items():
    return supabase.table("items").select("*").execute().data

def get_items_by_category(category_id=None):
    query = supabase.table("items").select("*")
    if category_id:
        query = query.eq("category_id", category_id)
    return query.execute().data

def calculate_next_bid(auction):
    # Giá tiếp theo = Giá hiện tại + Bước giá
    return auction.current_price + auction.bid_increment

def place_bid(user, auction):
    # 1. Tính giá tiếp theo
    next_bid = calculate_next_bid(auction)
    
    # 2. Tạo record Bid
    bid = Bid.objects.create(
        auction=auction,
        user=user,
        bid_amount=next_bid
    )
    
    # 3. Cập nhật giá hiện tại của phiên
    auction.current_price = next_bid
    auction.save()
    return bid

# services.py
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