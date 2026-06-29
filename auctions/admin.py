from django.contrib import admin
from django.apps import apps

# Lấy tất cả các model thuộc ứng dụng hiện tại
# Thay 'auctions' bằng tên app của bạn nếu cần
app_models = apps.get_app_config('auctions').get_models()

for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        # Bỏ qua nếu model đã được đăng ký thủ công ở đâu đó
        pass