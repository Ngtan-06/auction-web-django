from .supabase_client import supabase

def get_users():
    return supabase.table("users").select("*").execute().data

def create_user(username, email, role="buyer"):
    return supabase.table("users").insert({
        "username": username,
        "email": email,
        "role": role
    }).execute()

def update_user(user_id, data):
    return supabase.table("users").update(data).eq("id", user_id).execute()

def delete_user(user_id):
    return supabase.table("users").delete().eq("id", user_id).execute()
