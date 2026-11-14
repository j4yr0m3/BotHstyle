import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging

class NotificationManager:
    """
    Handles alert notifications via Email (SMTP) and Telegram Bot API.
    """
    def __init__(self, smtp_config: dict = None, telegram_config: dict = None):
        self.smtp_config = smtp_config or {}
        self.telegram_config = telegram_config or {}
        self.logger = logging.getLogger("NotificationManager")

    def send_email(self, subject: str, body: str, recipient: str) -> bool:
        if not self.smtp_config:
            self.logger.warning("Email notification skipped: SMTP config missing.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config.get('sender_email')
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_config.get('smtp_server', 'smtp.gmail.com'), self.smtp_config.get('smtp_port', 587))
            server.starttls()
            server.login(self.smtp_config.get('sender_email'), self.smtp_config.get('password'))
            server.send_message(msg)
            server.quit()
            self.logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False

    def send_telegram_message(self, message: str) -> bool:
        bot_token = self.telegram_config.get('bot_token')
        chat_id = self.telegram_config.get('chat_id')

        if not bot_token or not chat_id:
            self.logger.warning("Telegram notification skipped: Bot token or Chat ID missing.")
            return False

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info("Telegram message sent successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False