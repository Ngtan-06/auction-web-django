from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('auction/<int:auction_id>/', views.auction_detail_view, name='auction_detail'),
    path('auction/<int:auction_id>/bid/', views.place_bid_view, name='place_bid'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create/', views.create_auction_view, name='create_auction'),
    path('api/cron/trigger-auctions/', views.cron_trigger_auctions_view, name='cron_trigger_auctions'),
    path('api/cron/send-emails/', views.cron_send_emails, name='cron_send_emails'),
]
