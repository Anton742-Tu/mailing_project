from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    subject = models.CharField(max_length=200, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject


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
    message = models.ForeignKey(
        "Message", on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    clients = models.ManyToManyField("Client", verbose_name="Клиенты")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    period = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        default="once",
        verbose_name="Периодичность",
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
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


class MailingLog(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Ошибка"),
    ]

    mailing = models.ForeignKey(
        "Mailing", on_delete=models.CASCADE, verbose_name="Рассылка"
    )
    client = models.ForeignKey(
        "Client", on_delete=models.CASCADE, verbose_name="Клиент"
    )
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    server_response = models.TextField(
        blank=True, null=True, verbose_name="Ответ сервера"
    )
    error_message = models.TextField(
        blank=True, null=True, verbose_name="Сообщение об ошибке"
    )

    class Meta:
        verbose_name = "Лог рассылки"
        verbose_name_plural = "Логи рассылок"
        ordering = ["-attempt_time"]

    def __str__(self):
        return f"{self.mailing.title} - {self.client.email} ({self.status})"
