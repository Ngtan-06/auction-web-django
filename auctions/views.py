from django.shortcuts import render, redirect
import supabase
from .services import get_items, get_items_by_category

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
    return render(request, 'register.html')

def loginPage(request):
    return render(request, 'login.html')

def logoutPage(request):
    return redirect('register')

def artPage(request):
    return render(request, 'art.html')

def coinPage(request):
    return render(request, 'coin.html')

def fashionPage(request):
    return render(request, 'fashion.html')

def furniturePage(request):
    return render(request, 'furniture.html')

def jewelryPage(request):
    return render(request, 'jewelry.html')