from django.shortcuts import render, redirect
from .services import get_users, create_user, update_user, delete_user

def user_list(request):
    users = get_users()
    return render(request, "user_list.html", {"users": users})

def user_create(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        role = request.POST.get("role")
        create_user(username, email, role)
        return redirect("user_list")
    return render(request, "user_form.html")

def user_update(request, user_id):
    if request.method == "POST":
        data = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "role": request.POST.get("role"),
        }
        update_user(user_id, data)
        return redirect("user_list")
    return render(request, "user_form.html")

def user_delete(request, user_id):
    delete_user(user_id)
    return redirect("user_list")
