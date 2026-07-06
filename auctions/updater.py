import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

logger = logging.getLogger(__name__)

def check_and_finalize_auctions():
    # Vì hàm này chạy độc lập, ta phải import bên trong hàm để tránh lỗi sập vòng lặp import của Django
    from auctions.models import Auction
    from auctions.services import finalize_auction

    now = timezone.now()
    expired_auctions = Auction.objects.filter(status='active', end_time__lt=now)
    
    if expired_auctions.exists():
        logger.info(f"[Scheduler] Phát hiện {expired_auctions.count()} phiên đấu giá hết hạn.")
        for auction in expired_auctions:
            try:
                finalize_auction(auction)
                logger.info(f"[Scheduler] Đã đóng phiên đấu giá ID: {auction.id}")
            except Exception as e:
                logger.error(f"[Scheduler] Lỗi khi đóng phiên ID {auction.id}: {str(e)}")

def start():
    # RẤT QUAN TRỌNG CHO PRODUCTION: Tránh việc gunicorn sinh nhiều tiến trình (workers) làm chạy trùng lặp scheduler
    if os.environ.get('RUN_MAIN') == 'true' or 'gunicorn' in os.environ.get('SERVER_SOFTWARE', '').lower():
        scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone_name())
        
        # Cấu hình quét mỗi 60 giây một lần
        scheduler.add_job(check_and_finalize_auctions, 'interval', seconds=60, id='auction_updater_job', replace_existing=True)
        scheduler.start()
        logger.info("[Scheduler] Trình quét ngầm tự động đóng phiên đã kích hoạt thành công trên Render!")