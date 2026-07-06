import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from auctions.models import Auction
from auctions.services import finalize_auction

logger = logging.getLogger(__name__)

def check_and_finalize_auctions():
    """
    Hàm chạy ngầm: Tự động quét các phiên đấu giá 
    đang 'active' nhưng đã quá thời gian kết thúc.
    """
    now = timezone.now()
    # Tìm tất cả các phiên đấu giá còn hoạt động nhưng đã quá giờ kết thúc
    expired_auctions = Auction.objects.filter(status='active', end_time__lt=now)
    
    if expired_auctions.exists():
        logger.info(f"Phát hiện {expired_auctions.count()} phiên đấu giá hết hạn. Đang tiến hành đóng...")
        for auction in expired_auctions:
            try:
                finalize_auction(auction)
                logger.info(f"Đã đóng thành công phiên đấu giá ID: {auction.id}")
            except Exception as e:
                logger.error(f"Lỗi khi đóng phiên đấu giá ID {auction.id}: {str(e)}")
    else:
        logger.info("Không có phiên đấu giá nào hết hạn tại thời điểm này.")

class Command(BaseCommand):
    help = "Chạy trình quét ngầm để tự động đóng các phiên đấu giá hết hạn."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=timezone.get_current_timezone_name())
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Thiết lập lịch chạy: Quét mỗi phút một lần (60 giây)
        scheduler.add_job(
            check_and_finalize_auctions,
            trigger=CronTrigger(second="0"), # Chạy vào giây thứ 0 của mỗi phút
            id="check_and_finalize_auctions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Đã kích hoạt trình quét ngầm tự động đóng phiên đấu giá...")

        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
            logger.info("Đã dừng trình quét ngầm.")