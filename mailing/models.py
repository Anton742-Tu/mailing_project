from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class Client(models.Model):
    """Модель получателя рассылки"""
    email = models.EmailField(
        verbose_name='Email адрес',
        unique=True,
        max_length=255,
        help_text='Уникальный email адрес клиента'
    )
    full_name = models.CharField(
        verbose_name='Ф.И.О.',
        max_length=200,
        help_text='Полное имя клиента'
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        help_text='Дополнительная информация о клиенте'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True
    )
    is_active = models.BooleanField(
        verbose_name='Активный',
        default=True,
        help_text='Отметка для отключения клиента без удаления'
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']
        db_table = 'mailing_clients'

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def clean(self):
        """Валидация email перед сохранением"""
        super().clean()
        try:
            validate_email(self.email)
        except ValidationError:
            raise ValidationError({'email': 'Введите корректный email адрес'})

    def save(self, *args, **kwargs):
        """Переопределение save для автоматической валидации"""
        self.full_clean()
        super().save(*args, **kwargs)
