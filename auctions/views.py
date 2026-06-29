import supabase
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .services import place_bid, finalize_auction
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AuctionCreateForm, ItemForm
from .models import Auction, Notification, AuctionResult

def item_detail(request, item_id):
    # Lấy dữ liệu item từ Supabase
    item = supabase.table("items").select("*").eq("id", item_id).execute().data
    if item:
        item = item[0]
    else:
        item = None
    return render(request, "item_detail.html", {"item": item})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đăng ký thành công! Bạn có thể đăng nhập ngay.')
            return redirect('login')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@role_required(['seller'])
def create_auction_view(request):
    if request.method == 'POST':
        item_form = ItemForm(request.POST)
        auction_form = AuctionCreateForm(request.POST)
        if item_form.is_valid() and auction_form.is_valid():
            # Lưu item
            item = item_form.save(commit=False)
            item.seller = request.user
            item.save()
            
            # Lưu auction
            auction = auction_form.save(commit=False)
            auction.item = item
            auction.current_price = auction.start_price
            auction.status = 'active'
            auction.save()
            return redirect('dashboard') # Đảm bảo bạn đã có url 'dashboard'
    else:
        item_form = ItemForm()
        auction_form = AuctionCreateForm()
    
    return render(request, 'create_auction.html', {
        'item_form': item_form, 
        'auction_form': auction_form
    })

def home_view(request):
    # Lấy tất cả các phiên đấu giá đang diễn ra
    auctions = Auction.objects.filter(status='active').select_related('item')

    # Các phiên sắp tới (Pending hoặc đã tạo nhưng chưa đến giờ)
    upcoming_auctions = Auction.objects.filter(start_time__gt=timezone.now())
    return render(request, 'home.html', {'auctions': auctions, 'upcoming_auctions': upcoming_auctions})

def auction_detail_view(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    # Kiểm tra nếu phiên còn 'active' nhưng đã quá giờ
    if auction.status == 'active' and timezone.now() > auction.end_time:
        finalize_auction(auction)
        # Refresh lại đối tượng auction sau khi đã update status trong service
        auction.refresh_from_db()
    # Lấy lịch sử đấu giá, sắp xếp theo thời gian mới nhất
    bids = auction.bids.all().order_by('-bid_time')
    
    return render(request, 'auction_detail.html', {
        'auction': auction,
        'bids': bids
    })

@login_required
def place_bid_view(request, auction_id):
    if request.method == 'POST':
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Kiểm tra thời gian
        from django.utils import timezone
        if timezone.now() > auction.end_time:
            messages.error(request, "Phiên đấu giá đã kết thúc!")
            return redirect('auction_detail', auction_id=auction.id)

        # Đặt giá theo bước giá
        place_bid(request.user, auction)
        messages.success(request, "Đặt giá thành công!")
        
        return redirect('auction_detail', auction_id=auction.id)
    
@login_required
def dashboard_view(request):
    # Lấy thông báo chưa đọc của người dùng
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    # Lấy kết quả đấu giá (nếu là winner)
    won_auctions = AuctionResult.objects.filter(winner=request.user).order_by('-created_at')
    
    return render(request, 'dashboard.html', {
        'notifications': notifications,
        'won_auctions': won_auctions
    })

@login_required
def mark_as_read(request, notification_id):
    note = Notification.objects.get(id=notification_id, user=request.user)
    note.is_read = True
    note.save()
    return redirect('dashboard')