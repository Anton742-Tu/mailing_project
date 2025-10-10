from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Очищает весь кеш приложения"

    def handle(self, *args, **options):
        self.stdout.write("🔄 Очищаем кеш...")

        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("✅ Весь кеш успешно очищен!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка при очистке кеша: {e}"))
