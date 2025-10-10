from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing


class Command(BaseCommand):
    help = "Обновление статусов рассылок по времени"

    def handle(self, *args, **options):
        now = timezone.now()
        updated_count = 0

        # Обновляем статусы рассылок
        for mailing in Mailing.objects.all():
            _ = mailing.status

            if mailing.status == "created" and mailing.start_time <= now:
                mailing.status = "started"
                mailing.save()
                updated_count += 1
                self.stdout.write(f"🟢 Рассылка #{mailing.id} переведена в статус 'Запущена'")

            elif mailing.status == "started" and now > mailing.end_time:
                mailing.status = "completed"
                mailing.save()
                updated_count += 1
                self.stdout.write(f"🔴 Рассылка #{mailing.id} переведена в статус 'Завершена'")

        self.stdout.write(self.style.SUCCESS(f"✅ Обновлено статусов: {updated_count}"))
