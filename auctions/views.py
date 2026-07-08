import os
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .services import place_bid, finalize_auction, check_and_update_auctions
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AuctionCreateForm, ItemForm
from .models import Auction, Category, Notification, AuctionResult

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
        item_form = ItemForm(request.POST, request.FILES)
        auction_form = AuctionCreateForm(request.POST)
        if item_form.is_valid() and auction_form.is_valid():
            with transaction.atomic():
                # Lưu item
                item = item_form.save(commit=False)
                item.seller = request.user
                item.save()
                
                # Lưu auction
                auction = auction_form.save(commit=False)
                auction.item = item
                auction.current_price = auction.start_price
                auction.status = 'active' if auction.start_time <= timezone.now() else 'pending'
                auction.save()
            return redirect('home')
    else:
        item_form = ItemForm()
        auction_form = AuctionCreateForm()
    
    return render(request, 'create_auction.html', {
        'item_form': item_form, 
        'auction_form': auction_form
    })

def home_view(request):
    categories = Category.objects.all()
    # Lấy tất cả các phiên đấu giá đang diễn ra
    auctions = Auction.objects.filter(status='active').order_by('end_time')
    # Lấy các phiên đấu giá sắp tới
    upcoming_auctions = Auction.objects.filter(start_time__gt=timezone.now()).order_by('start_time')
    # Lọc theo từ khóa (tìm trong tên item)
    query = request.GET.get('q')
    # Lọc theo danh mục
    category_id = request.GET.get('category')
    if query:
        auctions = auctions.filter(item__name__icontains=query)
        upcoming_auctions = upcoming_auctions.filter(item__name__icontains=query)

    if category_id:
        auctions = auctions.filter(item__category__id=category_id)
        upcoming_auctions = upcoming_auctions.filter(item__category__id=category_id)
    return render(request, 'home.html', {'auctions': auctions,
                                          'upcoming_auctions': upcoming_auctions,
                                          'categories': categories})

def auction_detail_view(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    bids = auction.bids.all().order_by('-bid_time')
    
    return render(request, 'auction_detail.html', {
        'auction': auction,
        'bids': bids
    })

@login_required
def place_bid_view(request, auction_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ.'}, status=400)

    auction = get_object_or_404(Auction, id=auction_id)
    
    # Kiểm tra 1: Chặn nếu user đã là người đặt giá cao nhất
    if auction.current_bidder == request.user:
        return JsonResponse({'success': False, 'message': 'Bạn đang giữ giá cao nhất!'}, status=400)
        
    # Kiểm tra 2: Chặn nếu phiên đấu giá đã kết thúc
    if timezone.now() > auction.end_time or auction.status != 'active':
        return JsonResponse({'success': False, 'message': 'Phiên đấu giá này đã kết thúc!'}, status=400)

    try:
        # Gọi hàm xử lý từ service.py (Hàm này đã có sẵn logic gửi sang WebSocket)
        place_bid(request.user, auction)
        return JsonResponse({'success': True, 'message': 'Đặt giá thành công!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'}, status=500)
    
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

def cron_trigger_auctions_view(request):
    provided_token = request.GET.get('token')
    
    # Mã bí mật lưu ở biến môi trường Environment Variable (mặc định lấy chuỗi tạm nếu dev local)
    secret_token = os.getenv('CRON_SECRET_TOKEN')

    # Kiểm tra tính hợp lệ
    if not provided_token or provided_token != secret_token:
        return JsonResponse({'success': False, 'message': 'Unauthorized access'}, status=403)

    # Thực hiện quét database
    result = check_and_update_auctions()
    
    return JsonResponse({
        'success': True,
        'message': 'Cập nhật các phiên đấu giá thành công!',
        'data': result
    })