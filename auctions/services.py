from .supabase_client import supabase
import hashlib

# Lấy danh sách sản phẩm từ bảng items
def get_items():
    return supabase.table("items").select("*").execute().data

def get_items_by_category(category_id=None):
    query = supabase.table("items").select("*")
    if category_id:
        query = query.eq("category_id", category_id)
    return query.execute().data

def create_user(username, email, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return supabase.table("users").insert({
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "role": "bidder"
    }).execute()

def authenticate_user(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    result = supabase.table("users").select("*").eq("username", username).eq("password_hash", password_hash).execute()
    if result.data:
        return result.data[0]
    return None