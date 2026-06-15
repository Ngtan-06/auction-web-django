from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<int:category_id>/", views.category_view, name="category_view"),
    path("items/<int:item_id>/", views.item_detail, name="item_detail"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
