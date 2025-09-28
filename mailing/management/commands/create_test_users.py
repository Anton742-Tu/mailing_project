from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Client, Mailing, Message


class Command(BaseCommand):
    help = "Создает тестовых пользователей с разными ролями"

    def handle(self, *args, **options):
        # Получаем группы
        try:
            user_group = Group.objects.get(name="Пользователь")
            manager_group = Group.objects.get(name="Менеджер")
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Сначала создайте группы: python manage.py create_groups"))
            return

        # Создаем обычного пользователя
        user1, created = User.objects.get_or_create(
            username="test_user", defaults={"email": "user@example.com", "first_name": "Иван", "last_name": "Петров"}
        )
        if created:
            user1.set_password("test123")
            user1.save()
            user1.groups.add(user_group)
            self.create_user_data(user1, "Первый")
            self.stdout.write(f"✅ Создан пользователь: {user1.username}")

        # Создаем второго пользователя
        user2, created = User.objects.get_or_create(
            username="test_user2",
            defaults={"email": "user2@example.com", "first_name": "Мария", "last_name": "Сидорова"},
        )
        if created:
            user2.set_password("test123")
            user2.save()
            user2.groups.add(user_group)
            self.create_user_data(user2, "Второй")
            self.stdout.write(f"✅ Создан пользователь: {user2.username}")

        # Создаем менеджера
        manager, created = User.objects.get_or_create(
            username="manager",
            defaults={"email": "manager@example.com", "first_name": "Алексей", "last_name": "Менеджеров"},
        )
        if created:
            manager.set_password("test123")
            manager.save()
            manager.groups.add(manager_group)
            self.stdout.write(f"✅ Создан менеджер: {manager.username}")

        self.stdout.write(self.style.SUCCESS("🎉 Тестовые пользователи созданы!"))
        self.stdout.write("🔑 Логины и пароли:")
        self.stdout.write("   Пользователь 1: test_user / test123")
        self.stdout.write("   Пользователь 2: test_user2 / test123")
        self.stdout.write("   Менеджер: manager / test123")

    def create_user_data(self, user, user_type):
        """Создает тестовые данные для пользователя"""
        # Клиенты
        client1 = Client.objects.create(
            email=f"client1_{user.username}@example.com",
            full_name=f"Клиент {user_type} 1",
            comment=f"Клиент пользователя {user.username}",
            owner=user,
        )

        client2 = Client.objects.create(
            email=f"client2_{user.username}@example.com",
            full_name=f"Клиент {user_type} 2",
            comment=f"Еще один клиент {user.username}",
            owner=user,
        )

        # Сообщения
        message1 = Message.objects.create(
            subject=f"Тестовое сообщение от {user.username}",
            body=f"Это тестовое сообщение от пользователя {user.username}.",
            owner=user,
        )

        message2 = Message.objects.create(
            subject=f"Второе сообщение от {user.username}",
            body=f"Еще одно сообщение от пользователя {user.username}.",
            owner=user,
        )

        # Рассылки
        mailing1 = Mailing.objects.create(
            title=f"Тестовая рассылка {user_type}",
            message=message1,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=7),
            owner=user,
        )
        mailing1.clients.add(client1, client2)

        mailing2 = Mailing.objects.create(
            title=f"Вторая рассылка {user_type}",
            message=message2,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=30),
            owner=user,
        )
        mailing2.clients.add(client1)
