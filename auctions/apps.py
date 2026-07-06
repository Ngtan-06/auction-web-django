from django.apps import AppConfig


class AuctionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auctions'

    def ready(self):
        # Gọi trình quét ngầm hoạt động khi ứng dụng sẵn sàng
        from . import updater
        updater.start()
