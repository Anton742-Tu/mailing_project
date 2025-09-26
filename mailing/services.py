import logging
import smtplib
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText

from django.conf import settings
from django.utils import timezone

from .models import Mailing, MailingLog

# Настройка логгера
logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email"""

    def __init__(self):
        self.smtp_server = getattr(settings, "EMAIL_HOST", "smtp.gmail.com")
        self.smtp_port = getattr(settings, "EMAIL_PORT", 587)
        self.smtp_username = getattr(settings, "EMAIL_HOST_USER", "")
        self.smtp_password = getattr(settings, "EMAIL_HOST_PASSWORD", "")
        self.use_tls = getattr(settings, "EMAIL_USE_TLS", True)

    def send_email(self, client_email, subject, body):
        """Отправка email"""
        try:
            # Создание сообщения
            msg = MimeMultipart()
            msg["From"] = self.smtp_username
            msg["To"] = client_email
            msg["Subject"] = subject

            # Добавление тела сообщения
            msg.attach(MimeText(body, "plain", "utf-8"))

            # Подключение к серверу и отправка
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)

            if self.use_tls:
                server.starttls()

            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            text = msg.as_string()
            server.sendmail(self.smtp_username, client_email, text)
            server.quit()

            logger.info(f"Email успешно отправлен на {client_email}")
            return True, "Email sent successfully"

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Ошибка аутентификации: {e}"
            logger.error(error_msg)
            return False, error_msg

        except smtplib.SMTPException as e:
            error_msg = f"Ошибка SMTP: {e}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Неожиданная ошибка: {e}"
            logger.error(error_msg)
            return False, error_msg


def send_mailing(mailing_id):
    """Отправка рассылки по ID"""
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        email_service = EmailService()

        # Проверка времени рассылки
        now = timezone.now()
        if not (mailing.start_time <= now <= mailing.end_time and mailing.is_active):
            logger.warning(f"Рассылка {mailing_id} не активна в настоящее время")
            return False, "Рассылка не активна"

        success_count = 0
        failed_count = 0

        for client in mailing.clients.all():
            try:
                success, response = email_service.send_email(
                    client.email, mailing.message.subject, mailing.message.body
                )

                # Создание лога
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status="success" if success else "failed",
                    server_response=response if success else None,
                    error_message=response if not success else None,
                )

                if success:
                    success_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                # Логирование ошибки для конкретного клиента
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status="failed",
                    error_message=str(e),
                )
                failed_count += 1
                logger.error(f"Ошибка отправки клиенту {client.email}: {e}")

        # Обновление статуса рассылки
        if success_count > 0:
            mailing.status = "started"
            mailing.save()

        logger.info(
            f"Рассылка {mailing_id} завершена: {success_count} успешно, {failed_count} с ошибками"
        )
        return True, f"Отправлено: {success_count}, Ошибок: {failed_count}"

    except Mailing.DoesNotExist:
        error_msg = f"Рассылка {mailing_id} не найдена"
        logger.error(error_msg)
        return False, error_msg

    except Exception as e:
        error_msg = f"Ошибка отправки рассылки {mailing_id}: {e}"
        logger.error(error_msg)
        return False, error_msg


def get_mailing_stats(mailing_id):
    """Получение статистики по рассылке"""
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        logs = MailingLog.objects.filter(mailing=mailing)

        stats = {
            "total_clients": mailing.clients.count(),
            "success_count": logs.filter(status="success").count(),
            "failed_count": logs.filter(status="failed").count(),
            "last_attempt": logs.order_by("-attempt_time").first(),
        }

        if stats["total_clients"] > 0:
            stats["success_rate"] = (
                stats["success_count"] / stats["total_clients"]
            ) * 100
        else:
            stats["success_rate"] = 0

        return stats

    except Mailing.DoesNotExist:
        return None
