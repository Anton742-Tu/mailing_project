from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = "Отправка конкретной рассылки по ID"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int, help="ID рассылки для отправки")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Принудительная отправка, даже если время не подходит",
        )

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]
        force_send = options["force"]

        try:
            mailing = Mailing.objects.get(id=mailing_id)

            self.stdout.write(f"📧 Информация о рассылке:")
            self.stdout.write(f"   ID: {mailing.id}")
            self.stdout.write(f"   Название: {mailing.title}")
            self.stdout.write(f"   Статус: {mailing.get_status_display()}")
            self.stdout.write(f"   Клиентов: {mailing.clients.count()}")
            self.stdout.write(f"   Время начала: {mailing.start_time}")
            self.stdout.write(f"   Время окончания: {mailing.end_time}")

            # Проверка времени рассылки
            now = timezone.now()
            if not force_send and not mailing.is_active_now:
                self.stdout.write(
                    self.style.WARNING("⚠️  Рассылка не активна в настоящее время")
                )
                self.stdout.write(f"   Сейчас: {now}")
                self.stdout.write(
                    f"   Активна с: {mailing.start_time} по {mailing.end_time}"
                )

                response = input("Отправить принудительно? (y/n): ")
                if response.lower() != "y":
                    self.stdout.write("❌ Отправка отменена")
                    return

            self.stdout.write("🚀 Запуск отправки...")

            success, message = send_mailing(mailing_id)

            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Рассылка успешно отправлена!")
                )
                self.stdout.write(f"   Результат: {message}")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Ошибка отправки рассылки"))
                self.stdout.write(f"   Ошибка: {message}")

        except Mailing.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Рассылка с ID {mailing_id} не найдена")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Неожиданная ошибка: {str(e)}"))
