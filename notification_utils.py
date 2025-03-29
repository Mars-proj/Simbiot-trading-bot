import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from utils import logger_main, logger_debug
from config import NOTIFICATION_SETTINGS

async def send_telegram_notification(message):
    if not NOTIFICATION_SETTINGS['telegram']['enabled']:
        logger_main.debug("Telegram уведомления отключены")
        return
    bot_token = NOTIFICATION_SETTINGS['telegram']['bot_token']
    chat_id = NOTIFICATION_SETTINGS['telegram']['chat_id']
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    async with aiohttp.ClientSession() as session:
        try:
            logger_main.debug(f"Отправка Telegram уведомления: {message}")
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    logger_main.error(f"Не удалось отправить Telegram уведомление: {await response.text()}")
                else:
                    logger_main.debug("Telegram уведомление успешно отправлено")
        except Exception as e:
            logger_main.error(f"Ошибка при отправке Telegram уведомления: {str(e)}")

async def send_email_notification(subject, message):
    if not NOTIFICATION_SETTINGS['email']['enabled']:
        logger_main.debug("Email уведомления отключены")
        return
    smtp_server = NOTIFICATION_SETTINGS['email']['smtp_server']
    smtp_port = NOTIFICATION_SETTINGS['email']['smtp_port']
    sender_email = NOTIFICATION_SETTINGS['email']['sender_email']
    sender_password = NOTIFICATION_SETTINGS['email']['sender_password']
    receiver_email = NOTIFICATION_SETTINGS['email']['receiver_email']
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    try:
        logger_main.debug(f"Отправка Email уведомления: {subject}")
        # Используем run_in_executor для асинхронного выполнения
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: send_email_smtp(smtp_server, smtp_port, sender_email, sender_password, receiver_email, msg))
        logger_main.debug("Email уведомление успешно отправлено")
    except Exception as e:
        logger_main.error(f"Ошибка при отправке Email уведомления: {str(e)}")

def send_email_smtp(smtp_server, smtp_port, sender_email, sender_password, receiver_email, msg):
    """Синхронная функция для отправки email через SMTP"""
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

async def notify_trade(trade_log):
    required_keys = ['user_id', 'symbol', 'side', 'amount', 'order_type', 'price', 'exchange', 'timestamp']
    missing_keys = [key for key in required_keys if key not in trade_log]
    if missing_keys:
        logger_main.error(f"В trade_log отсутствуют обязательные ключи: {missing_keys}")
        return
    message = (
        f"Торговая операция выполнена!\n"
        f"Пользователь: {trade_log['user_id']}\n"
        f"Символ: {trade_log['symbol']}\n"
        f"Сторона: {trade_log['side']}\n"
        f"Количество: {trade_log['amount']}\n"
        f"Тип ордера: {trade_log['order_type']}\n"
        f"Цена: {trade_log['price']}\n"
        f"Stop-цена: {trade_log.get('stop_price', 'N/A')}\n"
        f"PNL: {trade_log.get('pnl', 'N/A')}\n"
        f"ROI: {trade_log.get('roi', 'N/A')}\n"
        f"Текущий депозит: {trade_log.get('current_deposit', 'N/A')} USDT\n"
        f"Просадка: {trade_log.get('drawdown', 0):.2%}\n"
        f"Биржа: {trade_log['exchange']}\n"
        f"Время: {trade_log['timestamp']}"
    )
    logger_main.debug(f"Формирование уведомления о торговой операции: {message}")
    await asyncio.gather(
        send_telegram_notification(message),
        send_email_notification("Новая торговая операция", message)
    )
