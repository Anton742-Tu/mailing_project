from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, MailingLog

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, MailingLog


@shared_task
def send_mailing_task(mailing_id):
    """
    Задача для отправки рассылки
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        print(f"📧 Отправка рассылки: {mailing.title}")

        success_count = 0
        error_count = 0

        for client in mailing.clients.all():
            try:
                # Получаем тему и тело сообщения
                if hasattr(mailing, 'message') and mailing.message:
                    subject = mailing.message.subject
                    body = mailing.message.body
                else:
                    # Резервный вариант
                    subject = f"Рассылка: {mailing.title}"
                    body = "Заходите на огонёк!"  # Ваше тестовое сообщение

                # Отправляем email
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                # Логируем успех с правильным полем server_response
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status='success',
                    server_response='Email отправлен успешно'
                )
                success_count += 1
                print(f"✅ Успешно: {client.email}")

            except Exception as e:
                # Логируем ошибку с правильными полями
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status='failed',
                    server_response='Ошибка отправки',
                    error_message=str(e)
                )
                error_count += 1
                print(f"❌ Ошибка для {client.email}: {e}")

        # Обновляем статус рассылки
        mailing.status = 'completed'
        mailing.save()

        result = f"Рассылка '{mailing.title}' завершена. Успешно: {success_count}, Ошибок: {error_count}"
        print(f"🎉 {result}")
        return result

    except Mailing.DoesNotExist:
        error_msg = "Рассылка не найдена"
        print(f"❌ {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Ошибка отправки: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


@shared_task
def check_pending_mailings():
    """
    Проверяет pending рассылки и запускает их отправку
    """
    from django.utils import timezone
    from .models import Mailing

    now = timezone.now()
    print(f"⏰ Проверка рассылок в: {now}")

    # Ищем рассылки которые должны запуститься
    pending_mailings = Mailing.objects.filter(
        start_time__lte=now
    ).exclude(status__in=['completed', 'running'])

    print(f"📋 Найдено рассылок для проверки: {pending_mailings.count()}")

    for mailing in pending_mailings:
        print(f"🎯 Рассылка для запуска: {mailing.title} (старт: {mailing.start_time}, статус: {mailing.status})")
        mailing.status = 'running'
        mailing.save()
        send_mailing_task.delay(mailing.id)
        print(f"🚀 Запущена рассылка: {mailing.title}")

    result = f"Проверено {pending_mailings.count()} рассылок"
    print(f"✅ {result}")
    return result
