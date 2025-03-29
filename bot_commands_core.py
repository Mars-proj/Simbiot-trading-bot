import asyncio
import ccxt.async_support as ccxt
from telegram import Update
from telegram.ext import ContextTypes
from logging_setup import logger_main, logger_exceptions
from bot_translations import get_translation
from bot_user_data import user_data, save_user_data, check_duplicate_keys, add_user_to_config
from bot_trading import start_trading
import importlib

# Хранилище времени первой ошибки для нерабочих ключей
invalid_keys = {}  # {user_id: {'timestamp': <время_первой_ошибки>, 'reason': <причина>}}

def save_config():
    """Сохраняет config_keys.py после изменений"""
    from config_keys import API_KEYS, PREFERRED_EXCHANGES
    with open('/root/trading_bot/config_keys.py', 'w') as f:
        f.write("# API keys for users and exchanges\n")
        f.write("API_KEYS = {\n")
        for uid, info in API_KEYS.items():
            f.write(f"    '{uid}': {{\n")
            for exchange, keys in info.items():
                f.write(f"        '{exchange}': {{\n")
                for key, value in keys.items():
                    if isinstance(value, str):
                        f.write(f"            '{key}': '{value}',\n")
                    else:
                        f.write(f"            '{key}': {value},\n")
                f.write("        },\n")
            f.write("    },\n")
        f.write("}\n\n")
        f.write("# Preferred exchanges for each user\n")
        f.write("PREFERRED_EXCHANGES = {\n")
        for uid, exchange in PREFERRED_EXCHANGES.items():
            f.write(f"    '{uid}': '{exchange}',\n")
        f.write("}\n\n")
        f.write("# Validate API keys\n")
        f.write("def validate_api_keys(logger_main):\n")
        f.write('    """Validates API keys to ensure they are properly configured"""\n')
        f.write("    for user, exchanges in API_KEYS.items():\n")
        f.write("        for exchange, creds in exchanges.items():\n")
        f.write("            if not creds.get('apiKey') or not creds.get('secret'):\n")
        f.write('                logger_main.error(f"Invalid API key configuration for user {user} on exchange {exchange}")\n')
        f.write('                raise ValueError(f"Invalid API key configuration for user {user} on exchange {exchange}")\n')
        f.write("\n")
        f.write("__all__ = ['API_KEYS', 'PREFERRED_EXCHANGES', 'validate_api_keys']\n")
    importlib.reload(importlib.import_module('config_keys'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = str(update.effective_user.id) if update.effective_user else None
    if not user_id:
        logger_main.warning("Не удалось определить user_id при выполнении команды /start")
        return
    user_data[user_id] = user_data.get(user_id, {'chat_id': user_id, 'language': 'ru'})
    save_user_data(user_data)
    await update.message.reply_text(get_translation(user_id, 'welcome', user_data))

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /register"""
    user_id = str(update.effective_user.id) if update.effective_user else None
    if not user_id:
        logger_main.warning("Не удалось определить user_id при выполнении команды /register")
        return
    await update.message.reply_text(get_translation(user_id, 'register_api_key', user_data))
    context.user_data['awaiting_api_key'] = True
    context.user_data['awaiting_api_secret'] = False

async def handle_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода ключей от пользователя"""
    user_id = str(update.effective_user.id) if update.effective_user else None
    if not user_id:
        logger_main.warning("Не удалось определить user_id при обработке ключей")
        return
    message_text = update.message.text.strip() if update.message and update.message.text else ""
    if context.user_data.get('awaiting_api_key', False):
        try:
            api_key = message_text
            if not api_key:
                await update.message.reply_text(get_translation(user_id, 'error_empty_key', user_data, key='api_key'))
                return
            context.user_data['api_key'] = api_key
            context.user_data['awaiting_api_key'] = False
            context.user_data['awaiting_api_secret'] = True
            await update.message.reply_text(get_translation(user_id, 'register_api_secret', user_data))
        except Exception as e:
            logger_main.error(f"Ошибка при получении api_key для {user_id}: {str(e)}")
            logger_exceptions.error(f"Ошибка при получении api_key: {str(e)}", exc_info=True)
            await update.message.reply_text(get_translation(user_id, 'error_register', user_data))
            context.user_data['awaiting_api_key'] = False
        return
    if context.user_data.get('awaiting_api_secret', False):
        try:
            api_secret = message_text
            if not api_secret:
                await update.message.reply_text(get_translation(user_id, 'error_empty_key', user_data, key='api_secret'))
                return
            api_key = context.user_data.get('api_key')
            if not api_key:
                await update.message.reply_text(get_translation(user_id, 'error_lost_key', user_data))
                context.user_data['awaiting_api_secret'] = False
                return
            if check_duplicate_keys(api_key, api_secret, user_id):
                await update.message.reply_text(get_translation(user_id, 'duplicate_keys', user_data))
                context.user_data['awaiting_api_secret'] = False
                context.user_data.pop('api_key', None)
                return
            success = add_user_to_config(user_id, api_key, api_secret)
            if not success:
                await update.message.reply_text(get_translation(user_id, 'error_register', user_data))
                return
            logger_main.info(f"Пользователь {user_id} зарегистрировал ключи для MEXC")
            await update.message.reply_text(get_translation(user_id, 'keys_registered', user_data))
            context.user_data['awaiting_api_secret'] = False
            context.user_data.pop('api_key', None)
            await start_trading(user_id, context)
        except Exception as e:
            logger_main.error(f"Ошибка при регистрации ключей для {user_id}: {str(e)}")
            logger_exceptions.error(f"Ошибка при регистрации ключей: {str(e)}", exc_info=True)
            await update.message.reply_text(get_translation(user_id, 'error_register', user_data))
            context.user_data['awaiting_api_secret'] = False
            context.user_data.pop('api_key', None)

async def lang_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /lang_ru"""
    user_id = str(update.effective_user.id) if update.effective_user else None
    if not user_id:
        logger_main.warning("Не удалось определить user_id при выполнении команды /lang_ru")
        return
    user_data[user_id] = user_data.get(user_id, {'chat_id': user_id, 'language': 'ru'})
    user_data[user_id]['language'] = 'ru'
    save_user_data(user_data)
    await update.message.reply_text(get_translation(user_id, 'language_set', user_data, language='Русский'))

async def lang_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /lang_en"""
    user_id = str(update.effective_user.id) if update.effective_user else None
    if not user_id:
        logger_main.warning("Не удалось определить user_id при выполнении команды /lang_en")
        return
    user_data[user_id] = user_data.get(user_id, {'chat_id': user_id, 'language': 'ru'})
    user_data[user_id]['language'] = 'en'
    save_user_data(user_data)
    await update.message.reply_text(get_translation(user_id, 'language_set', user_data, language='English'))

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /language"""
    user_id = str(update.effective_user.id) if update.effective_user else None
    if not user_id:
        logger_main.warning("Не удалось определить user_id при выполнении команды /language")
        return
    await update.message.reply_text(get_translation(user_id, 'language_select', user_data))

__all__ = ['start', 'register', 'handle_keys', 'lang_ru', 'lang_en', 'language']
