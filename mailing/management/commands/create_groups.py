from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailing.models import Client, Mailing, Message


class Command(BaseCommand):
    help = "Создает группы пользователей и назначает права"

    def handle(self, *args, **options):
        # Создаем группы
        user_group, created = Group.objects.get_or_create(name="Пользователь")
        manager_group, created = Group.objects.get_or_create(name="Менеджер")

        # Получаем ContentType для моделей
        client_content_type = ContentType.objects.get_for_model(Client)
        message_content_type = ContentType.objects.get_for_model(Message)
        mailing_content_type = ContentType.objects.get_for_model(Mailing)

        # Права для Пользователя
        user_permissions = [
            "add_client",
            "change_client",
            "delete_client",
            "view_client",
            "add_message",
            "change_message",
            "delete_message",
            "view_message",
            "add_mailing",
            "change_mailing",
            "delete_mailing",
            "view_mailing",
        ]

        for perm in user_permissions:
            permission = Permission.objects.get(
                content_type__in=[client_content_type, message_content_type, mailing_content_type], codename=perm
            )
            user_group.permissions.add(permission)

        # Права для Менеджера
        manager_permissions = [
            "view_client",
            "view_message",
            "view_mailing",
        ]

        for perm in manager_permissions:
            permission = Permission.objects.get(
                content_type__in=[client_content_type, message_content_type, mailing_content_type], codename=perm
            )
            manager_group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS("✅ Группы и права успешно созданы!"))
