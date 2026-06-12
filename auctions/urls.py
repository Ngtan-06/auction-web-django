from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<int:category_id>/", views.category_view, name="category_view"),
    path("items/<int:item_id>/", views.item_detail, name="item_detail"),
    path('register', views.register, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout', views.logoutPage, name='logout'),
    path('art', views.artPage, name='art'),
    path('coin', views.coinPage, name='coin'),
    path('fashion', views.fashionPage, name='fashion'),
    path('furniture', views.furniturePage, name='furniture'),
    path('jewelry', views.jewelryPage, name='jewelry'),
]
