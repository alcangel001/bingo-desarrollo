import logging
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import get_connection

logger = logging.getLogger(__name__)

class LoggingEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("LoggingEmailBackend initialized.")

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        num_sent = 0
        for email_message in email_messages:
            try:
                logger.info(f"Attempting to send email to: {email_message.to}, Subject: {email_message.subject}")
                # Use the parent's send_messages for actual sending
                # We send one by one to log individual failures
                sent = super().send_messages([email_message])
                if sent:
                    num_sent += sent
                    logger.info(f"Successfully sent email to: {email_message.to}, Subject: {email_message.subject}")
                else:
                    logger.warning(f"Failed to send email to: {email_message.to}, Subject: {email_message.subject} (returned 0)")
            except Exception as e:
                logger.error(f"Error sending email to {email_message.to}, Subject: {email_message.subject}: {e}", exc_info=True)
        return num_sent
