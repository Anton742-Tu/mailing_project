from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing


class Command(BaseCommand):
    help = "Список всех рассылок"

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            type=str,
            help="Фильтр по статусу (created/started/completed)",
        )
        parser.add_argument(
            "--active",
            action="store_true",
            help="Показать только активные рассылки",
        )

    def handle(self, *args, **options):
        mailings = Mailing.objects.all().order_by("-created_at")

        status_filter = options["status"]
        active_only = options["active"]

        if status_filter:
            mailings = mailings.filter(status=status_filter)
            self.stdout.write(f"📋 Рассылки со статусом '{status_filter}':")
        elif active_only:
            _ = timezone.now()
            mailings = [m for m in mailings if m.is_active_now]
            self.stdout.write("📋 Активные рассылки (сейчас):")
        else:
            self.stdout.write("📋 Все рассылки:")

        if not mailings:
            self.stdout.write("   Нет рассылок")
            return

        for mailing in mailings:
            status_color = {
                "created": self.style.WARNING,
                "started": self.style.SUCCESS,
                "completed": self.style.NOTICE,
            }.get(mailing.status, self.style.NOTICE)

            self.stdout.write(
                f"   #{mailing.id} {status_color(mailing.title)} "
                f"[{mailing.get_status_display()}] "
                f"- Клиентов: {mailing.clients.count()}"
            )
