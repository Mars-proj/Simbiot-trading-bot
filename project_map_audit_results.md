# Project Map: Audit Results

This file contains the results of the audit of the trading bot system's modules, including Core Trading Logic, Supporting Modules, and Additional Modules. Each entry includes the module name, its usage status, recommendations, useful settings (if any), and remarks.

## Audit Results
- **2025-03-28**: Модуль `json_handler.py` используется в системе (зависимость от `trade_executor_core.py`). Рекомендуется сохранить. Полезных настроек нет, но функции `dumps` и `loads` важны для сериализации данных. Замечание: В графе зависимостей указана связь `json_handler -> logging_setup`, но в коде этой зависимости нет. Удалена связь 2025-03-28.
- **2025-03-28**: Модуль `config_keys.py` используется в системе (зависимости от `start_trading_all.py`, `bot_user_data.py`). Рекомендуется сохранить. Полезные настройки: `API_KEYS` (хранит API-ключи для пользователей), `PREFERRED_EXCHANGES` (предпочтительные биржи для пользователей), `SUPPORTED_EXCHANGES` (список поддерживаемых бирж: `['mexc', 'binance', 'bybit', 'kucoin', 'okx']`).
- **2025-03-28**: Замечание: В графе зависимостей (`trading_bot_graph.dot`) отсутствует связь `config_keys.py` -> `logging_setup.py`, хотя `validate_api_keys` использует `logger_main`. Добавлена зависимость в граф 2025-03-28.
- **2025-03-29**: Модуль `bot_translations.py` удалён, так как Telegram-бот не интегрирован в текущую систему. Полезные настройки (переводы) сохранены ниже. Рекомендация: Восстановить модуль при интеграции Telegram-бота.

## Useful Settings from Removed Modules
- **bot_translations.py** (removed 2025-03-29):
