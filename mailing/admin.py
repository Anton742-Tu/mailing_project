from django.contrib import admin

from .models import Client, Mailing, MailingLog, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["email", "full_name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["email", "full_name"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["subject", "get_short_body", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["subject", "body"]
    list_editable = ["is_active"]

    def get_short_body(self, obj):
        return obj.get_short_body()

    get_short_body.short_description = "Текст сообщения"


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ("mailing", "client", "attempt_time", "status", "server_response")
    list_filter = ("status", "attempt_time", "mailing")
    search_fields = ("client__email", "mailing__title", "server_response")
    readonly_fields = ("attempt_time",)
    date_hierarchy = "attempt_time"

    def has_add_permission(self, request):
        return False  # Запрещаем ручное создание логов
