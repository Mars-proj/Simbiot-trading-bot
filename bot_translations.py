# Переводы для мультиязычности
TRANSLATIONS = {
    'ru': {
        'welcome': "Вас приветствует Meredian World, мы ваше будущее! ??\nНаша АИ поможет воплотить ваши мечты — торгуйте и зарабатывайте с помощью нашей системы на разных биржах.\nЧтобы начать, зарегистрируйте свои ключи с помощью команды /register.\nДоступные команды:\n/balance - посмотреть баланс и токены\n/pnl - посмотреть PNL за последние 24 часа\n/trend - узнать текущий тренд рынка\n/language - выбрать язык",
        'register_api_key': "Введите ваш api_key:",
        'register_api_secret': "Введите ваш api_secret:",
        'error_empty_key': "Ошибка: {key} не может быть пустым. Попробуй снова.",
        'error_lost_key': "Ошибка: api_key потерян. Пожалуйста, начни регистрацию заново с /register.",
        'duplicate_keys': "Ошибка: эти ключи уже зарегистрированы другим пользователем. Используй другие ключи.",
        'keys_registered': "Ключи успешно зарегистрированы! Теперь ты можешь торговать. Используй /balance, /pnl или /trend для получения информации.",
        'error_register': "Произошла ошибка при регистрации ключей. Попробуй снова.",
        'need_register': "Сначала зарегистрируй свои ключи с помощью команды /register.",
        'balance_empty': "Твой баланс пуст.\nОбщий баланс в USDT: {total_usdt:.2f} USDT",
        'balance': "Твой баланс:\n{balance}\nОбщий баланс в USDT: {total_usdt:.2f} USDT",
        'error_balance': "Произошла ошибка при получении баланса. Попробуй позже.",
        'error_auth': "Ошибка: ключи недействительны. Пожалуйста, зарегистрируй новые ключи с помощью /register.",
        'error_network': "Сетевая ошибка при получении баланса. Попробуй позже.",
        'pnl': "Твой PNL за последние 24 часа: {pnl:.2f} USDT",
        'error_pnl': "Произошла ошибка при получении PNL. Попробуй позже.",
        'trend_data_error': "Не удалось загрузить данные для {symbol}: {error}",
        'trend': "Текущий тренд (на основе BTC/USDT): {trend_info}",
        'error_trend': "Произошла ошибка при получении тренда. Попробуй позже.",
        'trade_error': "Произошла ошибка при запуске торговли. Попробуй позже.",
        'drawdown': "Торговля для {symbol} отменена из-за превышения просадки.",
        'data_error': "Не удалось загрузить данные для {symbol}: {error}",
        'trade': "Торговая операция выполнена!\nСимвол: {symbol}\nСторона: {side}\nКоличество: {amount}\nТип ордера: {order_type}\nЦена: {price}\nБиржа: {exchange}\nВремя: {timestamp}",
        'symbol_error': "Ошибка при обработке {symbol}: {error}",
        'symbols_error': "Ошибка при обработке символов: {error}",
        'language_select': "Выберите язык:\n1. Русский (/lang_ru)\n2. English (/lang_en)",
        'language_set': "Язык установлен: {language}"
    },
    'en': {
        'welcome': "Welcome to Meredian World, we are your future! ??\nOur AI will help make your dreams come true — trade and earn with our system on various exchanges.\nTo get started, register your keys with the /register command.\nAvailable commands:\n/balance - view balance and tokens\n/pnl - view PNL for the last 24 hours\n/trend - check the current market trend\n/language - select language",
        'register_api_key': "Enter your api_key:",
        'register_api_secret': "Enter your api_secret:",
        'error_empty_key': "Error: {key} cannot be empty. Try again.",
        'error_lost_key': "Error: api_key is lost. Please start registration again with /register.",
        'duplicate_keys': "Error: these keys are already registered by another user. Use different keys.",
        'keys_registered': "Keys successfully registered! Now you can trade. Use /balance, /pnl, or /trend to get information.",
        'error_register': "An error occurred while registering the keys. Try again.",
        'need_register': "First, register your keys using the /register command.",
        'balance_empty': "Your balance is empty.\nTotal balance in USDT: {total_usdt:.2f} USDT",
        'balance': "Your balance:\n{balance}\nTotal balance in USDT: {total_usdt:.2f} USDT",
        'error_balance': "An error occurred while retrieving the balance. Try again later.",
        'error_auth': "Error: invalid keys. Please register new keys using /register.",
        'error_network': "Network error while retrieving the balance. Try again later.",
        'pnl': "Your PNL for the last 24 hours: {pnl:.2f} USDT",
        'error_pnl': "An error occurred while retrieving PNL. Try again later.",
        'trend_data_error': "Failed to load data for {symbol}: {error}",
        'trend': "Current trend (based on BTC/USDT): {trend_info}",
        'error_trend': "An error occurred while retrieving the trend. Try again later.",
        'trade_error': "An error occurred while starting trading. Try again later.",
        'drawdown': "Trading for {symbol} canceled due to exceeding drawdown.",
        'data_error': "Failed to load data for {symbol}: {error}",
        'trade': "Trade executed!\nSymbol: {symbol}\nSide: {side}\nAmount: {amount}\nOrder type: {order_type}\nPrice: {price}\nExchange: {exchange}\nTime: {timestamp}",
        'symbol_error': "Error processing {symbol}: {error}",
        'symbols_error': "Error processing symbols: {error}",
        'language_select': "Select language:\n1. Русский (/lang_ru)\n2. English (/lang_en)",
        'language_set': "Language set: {language}"
    }
}

# Функция для получения перевода
def get_translation(user_id, key, user_data, **kwargs):
    language = user_data.get(user_id, {}).get('language', 'ru')  # По умолчанию русский
    translation = TRANSLATIONS.get(language, TRANSLATIONS['ru']).get(key, key)
    return translation.format(**kwargs)
