from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from .cache_utils import cache_model_method


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def can_edit(self, user):
        """Проверяет, может ли пользователь редактировать клиента"""
        return user == self.owner or user.groups.filter(name="Менеджер").exists()

    def can_delete(self, user):
        """Проверяет, может ли пользователь удалить клиента"""
        return user == self.owner


class Message(models.Model):
    subject = models.CharField(max_length=200, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject

    def can_edit(self, user):
        """Проверяет, может ли пользователь редактировать сообщение"""
        return user == self.owner or user.groups.filter(name="Менеджер").exists()

    def can_delete(self, user):
        """Проверяет, может ли пользователь удалить сообщение"""
        return user == self.owner


def can_disable(user):
    """Проверяет, может ли менеджер отключить рассылку"""
    return user.groups.filter(name="Менеджер").exists()


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    PERIOD_CHOICES = [
        ("once", "Однократно"),
        ("daily", "Ежедневно"),
        ("weekly", "Еженедельно"),
        ("monthly", "Ежемесячно"),
    ]

    title = models.CharField(max_length=200, verbose_name="Название рассылки")
    message = models.ForeignKey("Message", on_delete=models.CASCADE, verbose_name="Сообщение")
    clients = models.ManyToManyField("Client", verbose_name="Клиенты")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="once", verbose_name="Периодичность")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created", verbose_name="Статус")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_active_now(self):
        """Проверяет, активна ли рассылка в текущий момент"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.is_active

    def get_clients_count(self):
        return self.clients.count()

    get_clients_count.short_description = "Кол-во клиентов"

    def get_success_rate(self):
        """Процент успешных отправок"""
        total = self.get_total_attempts()
        if total > 0:
            return (self.get_success_count() / total) * 100
        return 0

    def can_edit(self, user):
        """Проверяет, может ли пользователь редактировать рассылку"""
        return user == self.owner or user.groups.filter(name="Менеджер").exists()

    def can_delete(self, user):
        """Проверяет, может ли пользователь удалить рассылку"""
        return user == self.owner

    @cache_model_method(timeout=60 * 10)  # Кешируем на 10 минут
    def get_success_count(self):
        """Количество успешных отправок для этой рассылки"""
        return self.mailinglog_set.filter(status="success").count()

    @cache_model_method(timeout=60 * 10)
    def get_failed_count(self):
        """Количество неуспешных отправок для этой рассылки"""
        return self.mailinglog_set.filter(status="failed").count()

    @cache_model_method(timeout=60 * 10)
    def get_total_attempts(self):
        """Общее количество попыток отправки"""
        return self.mailinglog_set.count()


class MailingLog(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Ошибка"),
    ]

    mailing = models.ForeignKey("Mailing", on_delete=models.CASCADE, verbose_name="Рассылка")
    client = models.ForeignKey("Client", on_delete=models.CASCADE, verbose_name="Клиент")
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ сервера")
    error_message = models.TextField(blank=True, null=True, verbose_name="Сообщение об ошибке")

    class Meta:
        verbose_name = "Лог рассылки"
        verbose_name_plural = "Логи рассылок"
        ordering = ["-attempt_time"]

    def __str__(self):
        return f"{self.mailing.title} - {self.client.email} ({self.status})"


# Статические методы для статистики
def get_user_statistics(user):
    """Статистика по всем рассылкам пользователя с простым кешированием"""
    cache_key = f"user_stats_{user.id}"

    # Пробуем получить из кеша
    cached_stats = cache.get(cache_key)
    if cached_stats is not None:
        return cached_stats

    # Если нет в кеше - вычисляем
    stats = _calculate_user_statistics(user)

    # Сохраняем в кеш на 5 минут
    cache.set(cache_key, stats, 300)

    return stats


def _calculate_user_statistics(user):
    """Внутренняя функция для расчета статистики"""
    from django.db.models import Count, Q

    user_mailings = Mailing.objects.filter(owner=user)

    total_mailings = user_mailings.count()
    active_mailings = user_mailings.filter(is_active=True).count()

    # Статистика по логам
    logs_stats = MailingLog.objects.filter(mailing__owner=user).aggregate(
        total_attempts=Count("id"),
        success_attempts=Count("id", filter=Q(status="success")),
        failed_attempts=Count("id", filter=Q(status="failed")),
    )

    return {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "completed_mailings": user_mailings.filter(status="completed").count(),
        "total_attempts": logs_stats["total_attempts"] or 0,
        "success_attempts": logs_stats["success_attempts"] or 0,
        "failed_attempts": logs_stats["failed_attempts"] or 0,
        "success_rate": (
            (logs_stats["success_attempts"] / logs_stats["total_attempts"] * 100)
            if logs_stats["total_attempts"] and logs_stats["total_attempts"] > 0
            else 0
        ),
    }
