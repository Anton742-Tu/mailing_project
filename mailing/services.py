import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from django.utils import timezone
from .models import Mailing, MailingLog

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'EMAIL_PORT', 587)
        self.smtp_username = getattr(settings, 'EMAIL_HOST_USER', '')
        self.smtp_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        self.use_tls = getattr(settings, 'EMAIL_USE_TLS', True)

    def send_email(self, client_email, subject, body):
        """Отправка email"""
        try:
            # Для тестирования - эмулируем отправку
            logger.info(f"📧 Эмуляция отправки email на {client_email}")

            # В реальном режиме раскомментируйте:
            """
            msg = MimeMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = client_email
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            text = msg.as_string()
            server.sendmail(self.smtp_username, client_email, text)
            server.quit()
            """

            # Эмуляция успешной отправки
            return True, "Email sent successfully (emulated)"

        except Exception as e:
            logger.error(f"❌ Ошибка отправки email: {e}")
            return False, str(e)


def send_mailing(mailing_id):
    """Отправка рассылки по ID"""
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        email_service = EmailService()

        # Обновляем статус на "Запущена" при первой отправке
        if mailing.status == 'created':
            mailing.status = 'started'
            mailing.save()

        success_count = 0
        failed_count = 0

        for client in mailing.clients.all():
            try:
                success, response = email_service.send_email(
                    client.email,
                    mailing.message.subject,
                    mailing.message.body
                )

                # Логирование
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status='success' if success else 'failed',
                    server_response=response if success else None,
                    error_message=response if not success else None
                )

                if success:
                    success_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status='failed',
                    error_message=str(e)
                )
                failed_count += 1

        # Проверяем завершение рассылки
        now = timezone.now()
        if now > mailing.end_time:
            mailing.status = 'completed'
            mailing.save()

        return True, f"Отправлено: {success_count}, Ошибок: {failed_count}"

    except Mailing.DoesNotExist:
        return False, f"Рассылка {mailing_id} не найдена"
    except Exception as e:
        return False, f"Ошибка отправки рассылки: {str(e)}"
