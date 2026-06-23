from .supabase_client import supabase
from django.contrib.auth.hashers import make_password
import hashlib

# Lấy danh sách sản phẩm từ bảng items
def get_items():
    return supabase.table("items").select("*").execute().data

def get_items_by_category(category_id=None):
    query = supabase.table("items").select("*")
    if category_id:
        query = query.eq("category_id", category_id)
    return query.execute().data
