# Notification settings
NOTIFICATION_SETTINGS = {
    'telegram': {
        'enabled': True,
        'bot_token': '7315917060:AAExPok4cty45sjXxbz9rs8wbrdLVwE8p_Y',
        'chat_id': '',  # Add your Telegram chat ID here to receive notifications
    },
    'email': {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'your_email@gmail.com',
        'sender_password': 'your_password',
        'receiver_email': 'receiver_email@gmail.com',
    }
}

# Validate notification settings
def validate_notification_settings(logger_main):
    """Validates notification settings to ensure they are properly configured"""
    if NOTIFICATION_SETTINGS['telegram']['enabled']:
        if not NOTIFICATION_SETTINGS['telegram']['bot_token']:
            logger_main.error("Telegram bot token is not set but Telegram notifications are enabled")
            raise ValueError("Telegram bot token is not set but Telegram notifications are enabled")
        if not NOTIFICATION_SETTINGS['telegram']['chat_id']:
            logger_main.warning("Telegram chat ID is not set; notifications will not be sent")
    if NOTIFICATION_SETTINGS['email']['enabled']:
        required_email_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'receiver_email']
        for field in required_email_fields:
            if not NOTIFICATION_SETTINGS['email'][field]:
                logger_main.error(f"Email notification field '{field}' is not set but email notifications are enabled")
                raise ValueError(f"Email notification field '{field}' is not set but email notifications are enabled")

__all__ = ['NOTIFICATION_SETTINGS', 'validate_notification_settings']
