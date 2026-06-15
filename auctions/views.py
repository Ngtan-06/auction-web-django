from django.shortcuts import render, redirect
from django.contrib import messages
import supabase
from .services import get_items, get_items_by_category, create_user, authenticate_user
from .forms import LoginForm, RegisterForm

def home(request):
    items = get_items_by_category()
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

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["password1"] != form.cleaned_data["password2"]:
                messages.error(request, "Mật khẩu không khớp.")
            else:
                create_user(
                    form.cleaned_data["username"],
                    form.cleaned_data["email"],
                    form.cleaned_data["password1"]
                )
                messages.success(request, "Đăng ký thành công, hãy đăng nhập.")
                return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate_user(form.cleaned_data["username"], form.cleaned_data["password"])
            if user:
                request.session["user"] = user
                messages.success(request, "Đăng nhập thành công.")
                return redirect("home")
            else:
                messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    request.session.flush()
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect("home")
