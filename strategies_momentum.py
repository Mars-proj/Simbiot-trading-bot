import pandas as pd
import numpy as np
import pandas_ta as ta
from utils import logger_main

def generate_momentum_signals(df, market_conditions=None, success_prob=None):
    """
    Генерирует сигналы для импульсной стратегии на основе RSI.
    Аргументы:
    - df: DataFrame с данными OHLCV
    - market_conditions: словарь с рыночными условиями (avg_volatility, avg_drop)
    - success_prob: вероятность успешности сделки (от 0 до 1), может быть None
    Возвращает:
    - сигнал: 1 (покупка), -1 (продажа), 0 (нет сигнала)
    """
    logger_main.debug("Генерация сигналов для импульсной стратегии")
    try:
        # Проверяем, достаточно ли данных
        if len(df) < 50:
            logger_main.warning("Недостаточно данных для генерации импульсных сигналов")
            return 0

        # Вычисляем волатильность для определения порогов
        df['returns'] = df['close'].pct_change()
        volatility = df['returns'].rolling(window=20).std().iloc[-1] * np.sqrt(252) if not df['returns'].empty else 0
        logger_main.debug(f"Текущая волатильность: {volatility:.4f}")

        # Вычисляем RSI
        df['rsi'] = ta.rsi(df['close'], length=14)
        current_rsi = df['rsi'].iloc[-1]
        logger_main.debug(f"Текущий RSI: {current_rsi:.2f}")

        # Динамические пороги RSI
        rsi_buy = 45 + (volatility * 5)  # Увеличиваем порог покупки с 40 до 45
        rsi_sell = 55 - (volatility * 5)  # Уменьшаем порог продажи с 60 до 55
        logger_main.debug(f"Динамические пороги RSI: покупка при RSI < {rsi_buy:.2f}, продажа при RSI > {rsi_sell:.2f}")

        # Корректируем пороги RSI на основе success_prob
        if success_prob is not None:
            if success_prob > 0.7:  # Высокая вероятность успешности
                rsi_buy *= 0.9  # Уменьшаем порог покупки (более агрессивно)
                rsi_sell *= 1.1  # Увеличиваем порог продажи (более агрессивно)
                logger_main.debug(f"Высокая вероятность успешности ({success_prob:.2f}), корректируем пороги RSI: покупка={rsi_buy:.2f}, продажа={rsi_sell:.2f}")
            elif success_prob < 0.3:  # Низкая вероятность успешности
                rsi_buy *= 1.1  # Увеличиваем порог покупки (более консервативно)
                rsi_sell *= 0.9  # Уменьшаем порог продажи (более консервативно)
                logger_main.debug(f"Низкая вероятность успешности ({success_prob:.2f}), корректируем пороги RSI: покупка={rsi_buy:.2f}, продажа={rsi_sell:.2f}")

        # Генерируем сигналы только на основе RSI
        if current_rsi < rsi_buy:
            logger_main.debug(f"Импульсный сигнал: покупка (RSI={current_rsi:.2f} < {rsi_buy:.2f})")
            return 1  # Покупка
        elif current_rsi > rsi_sell:
            logger_main.debug(f"Импульсный сигнал: продажа (RSI={current_rsi:.2f} > {rsi_sell:.2f})")
            return -1  # Продажа
        else:
            logger_main.debug(f"Нет импульсного сигнала (RSI={current_rsi:.2f})")
            return 0  # Нет сигнала

    except Exception as e:
        logger_main.error(f"Ошибка при генерации импульсных сигналов: {str(e)}")
        return 0

__all__ = ['generate_momentum_signals']
