import supabase
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .services import get_items_by_category, get_items
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def home(request):
    items = get_items()
    return render(request, "home.html", {"items": items})

def category_view(request, category_id):
    items = get_items_by_category(category_id)
    return render(request, "home.html", {"items": items, "category_id": category_id})

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