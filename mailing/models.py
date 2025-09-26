from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models


class Client(models.Model):
    """Модель получателя рассылки"""

    email = models.EmailField(verbose_name="Email адрес", unique=True, max_length=255)
    full_name = models.CharField(verbose_name="Ф.И.О.", max_length=200)
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    is_active = models.BooleanField(verbose_name="Активный", default=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    """Модель сообщения для рассылки"""

    subject = models.CharField(
        verbose_name="Тема письма",
        max_length=255,
        help_text="Краткое описание содержания письма",
    )
    body = models.TextField(
        verbose_name="Тело письма", help_text="Основное содержание сообщения"
    )
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    is_active = models.BooleanField(verbose_name="Активное", default=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.created_at.strftime('%d.%m.%Y')})"

    def get_short_body(self):
        """Короткое представление тела сообщения"""
        return self.body[:100] + "..." if len(self.body) > 100 else self.body
