"""
Notifications Module - Multi-channel notification system

Supports email, Telegram, and desktop notifications for backup events.
"""

import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, Optional

from loguru import logger

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from plyer import notification as desktop_notification

    DESKTOP_NOTIFICATION_AVAILABLE = True
except ImportError:
    DESKTOP_NOTIFICATION_AVAILABLE = False
    logger.warning("Desktop notifications not available - install with: pip install plyer")


class NotificationType(Enum):
    """Notification event types."""

    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"


@dataclass
class NotificationConfig:
    """Notification configuration."""

    # Email settings
    email_enabled: bool = False
    email_address: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True

    # Telegram settings
    telegram_enabled: bool = False
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    # Desktop settings
    desktop_enabled: bool = True

    # Event filters
    on_success: bool = True
    on_failure: bool = True
    on_warning: bool = True
    on_info: bool = False


class NotificationManager:
    """Manages multi-channel notifications."""

    def __init__(self, config: NotificationConfig):
        """Initialize notification manager.

        Args:
            config: NotificationConfig with settings
        """
        self.config = config
        logger.info("Notification manager initialized")

    def send_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Send notification through enabled channels.

        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            details: Optional additional details
        """
        # Check if this event type should be notified
        if not self._should_notify(notification_type):
            return

        logger.info(f"Sending {notification_type.value} notification: {title}")

        # Send through enabled channels
        if self.config.email_enabled:
            self._send_email(notification_type, title, message, details)

        if self.config.telegram_enabled:
            self._send_telegram(notification_type, title, message, details)

        if self.config.desktop_enabled:
            self._send_desktop(notification_type, title, message)

    def _should_notify(self, notification_type: NotificationType) -> bool:
        """Check if notification should be sent based on config.

        Args:
            notification_type: Type of notification

        Returns:
            True if notification should be sent
        """
        if notification_type == NotificationType.SUCCESS:
            return self.config.on_success
        elif notification_type == NotificationType.FAILURE:
            return self.config.on_failure
        elif notification_type == NotificationType.WARNING:
            return self.config.on_warning
        elif notification_type == NotificationType.INFO:
            return self.config.on_info
        return False

    def _send_email(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Send email notification.

        Args:
            notification_type: Type of notification
            title: Email subject
            message: Email body
            details: Optional additional details
        """
        if not all(
            [
                self.config.smtp_server,
                self.config.smtp_username,
                self.config.email_address,
            ]
        ):
            logger.warning("Email configuration incomplete - skipping email notification")
            return

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.config.smtp_username
            msg["To"] = self.config.email_address
            msg["Subject"] = f"[Nimbus] {title}"

            # Build email body
            body = f"{message}\n\n"

            if details:
                body += "Details:\n"
                for key, value in details.items():
                    body += f"  {key}: {value}\n"

            body += f"\n---\nNimbus Backup System\n{notification_type.value.upper()} notification"

            msg.attach(MIMEText(body, "plain"))

            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)

            if self.config.smtp_use_tls:
                server.starttls()

            if self.config.smtp_password:
                server.login(self.config.smtp_username, self.config.smtp_password)

            server.send_message(msg)
            server.quit()

            logger.info(f"Email notification sent to {self.config.email_address}")

        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    def _send_telegram(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Send Telegram notification.

        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            details: Optional additional details
        """
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests library not available - skipping Telegram notification")
            return

        if not all([self.config.telegram_token, self.config.telegram_chat_id]):
            logger.warning("Telegram configuration incomplete - skipping Telegram notification")
            return

        try:
            # Build message
            emoji = self._get_emoji(notification_type)
            text = f"{emoji} *{title}*\n\n{message}"

            if details:
                text += "\n\n*Details:*\n"
                for key, value in details.items():
                    text += f"  • {key}: `{value}`\n"

            # Send via Telegram Bot API
            url = f"https://api.telegram.org/bot{self.config.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.config.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info("Telegram notification sent")
            else:
                logger.error(f"Telegram API error: {response.text}")

        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

    def _send_desktop(self, notification_type: NotificationType, title: str, message: str):
        """Send desktop notification.

        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
        """
        if not DESKTOP_NOTIFICATION_AVAILABLE:
            logger.debug("Desktop notifications not available")
            return

        try:
            desktop_notification.notify(
                title=f"Nimbus - {title}",
                message=message,
                app_name="Nimbus",
                timeout=10,
            )

            logger.debug("Desktop notification sent")

        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")

    def _get_emoji(self, notification_type: NotificationType) -> str:
        """Get emoji for notification type.

        Args:
            notification_type: Type of notification

        Returns:
            Emoji string
        """
        emojis = {
            NotificationType.SUCCESS: "✅",
            NotificationType.FAILURE: "❌",
            NotificationType.WARNING: "⚠️",
            NotificationType.INFO: "ℹ️",
        }
        return emojis.get(notification_type, "📢")

    def send_backup_success(self, stats: Dict[str, Any]):
        """Send backup success notification.

        Args:
            stats: Backup statistics
        """
        self.send_notification(
            NotificationType.SUCCESS,
            "Backup Completed Successfully",
            f"Backup completed with {stats.get('backed_up_files', 0)} files backed up.",
            stats,
        )

    def send_backup_failure(self, error: str, details: Optional[Dict[str, Any]] = None):
        """Send backup failure notification.

        Args:
            error: Error message
            details: Optional error details
        """
        self.send_notification(
            NotificationType.FAILURE,
            "Backup Failed",
            f"Backup failed with error: {error}",
            details,
        )

    def send_backup_warning(self, warning: str, details: Optional[Dict[str, Any]] = None):
        """Send backup warning notification.

        Args:
            warning: Warning message
            details: Optional warning details
        """
        self.send_notification(NotificationType.WARNING, "Backup Warning", warning, details)
