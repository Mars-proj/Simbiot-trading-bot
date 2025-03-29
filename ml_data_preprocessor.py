import pandas as pd
import numpy as np
import pandas_ta as ta
from utils import logger_main, log_exception
from data_fetcher import fetch_ohlcv
from trade_pool import get_recent_trades

class MLDataPreprocessor:
    def __init__(self):
        self.lookback_period = 500  # Увеличиваем до 500 свечей для OHLCV
        self.indicators = ['rsi', 'macd', 'bollinger']  # Список индикаторов
        self.trade_limit = 1000  # Максимальное количество сделок для анализа

    async def fetch_and_prepare_data(self, exchange, symbol):
        """Получает и подготавливает данные для ML-моделей"""
        logger_main.debug(f"Подготовка данных для {symbol} на {exchange.id}")
        try:
            # Получаем OHLCV-данные
            logger_main.debug(f"Получение OHLCV для {symbol}, timeframe=4h, limit={self.lookback_period}")
            ohlcv = await fetch_ohlcv(exchange, symbol, timeframe='4h', limit=self.lookback_period)
            if ohlcv is None or ohlcv.empty:
                logger_main.warning(f"OHLCV данные для {symbol} пусты или не загружены")
                return None
            logger_main.debug(f"OHLCV данные для {symbol} получены, длина: {len(ohlcv)}")

            # Получаем сделки
            logger_main.debug(f"Получение последних {self.trade_limit} сделок")
            trades = await get_recent_trades(limit=self.trade_limit)
            trades_df = pd.DataFrame(trades)
            logger_main.debug(f"Получено сделок: {len(trades_df)}")

            # Подготовка OHLCV-данных
            ohlcv_df = self._prepare_ohlcv(ohlcv)
            if ohlcv_df is None or ohlcv_df.empty:
                logger_main.warning(f"Не удалось подготовить OHLCV данные для {symbol}")
                return None

            # Подготовка данных о сделках
            trades_df = self._prepare_trades(trades_df, symbol)
            if trades_df is None:
                logger_main.warning(f"Не удалось подготовить данные о сделках для {symbol}")
                return None

            # Объединяем данные
            combined_data = self._combine_data(ohlcv_df, trades_df)
            if combined_data is None:
                logger_main.warning(f"Не удалось объединить данные для {symbol}")
                return None

            logger_main.debug(f"Данные для {symbol} успешно подготовлены, длина: {len(combined_data)}")
            return combined_data

        except Exception as e:
            logger_main.error(f"Ошибка при подготовке данных для {symbol}: {str(e)}")
            log_exception(f"Ошибка при подготовке данных: {str(e)}", e)
            return None

    def _prepare_ohlcv(self, ohlcv):
        """Подготавливает OHLCV-данные, добавляет индикаторы"""
        logger_main.debug("Подготовка OHLCV-данных")
        try:
            df = ohlcv.copy()
            logger_main.debug(f"Исходная длина OHLCV: {len(df)}")

            # Рассчитываем индикаторы
            df['rsi'] = ta.rsi(df['close'], length=14)
            macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
            df['macd'] = macd['MACD_12_26_9']
            df['macd_signal'] = macd['MACDs_12_26_9']
            bbands = ta.bbands(df['close'], length=20)
            df['bb_upper'] = bbands['BBU_20_2.0']
            df['bb_middle'] = bbands['BBM_20_2.0']
            df['bb_lower'] = bbands['BBL_20_2.0']

            # Рассчитываем волатильность
            df['returns'] = df['close'].pct_change()
            df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)

            # Удаляем строки с NaN
            df = df.dropna()
            logger_main.debug(f"Длина OHLCV после удаления NaN: {len(df)}")
            if df.empty:
                logger_main.warning("OHLCV данные пусты после удаления NaN")
                return None

            return df
        except Exception as e:
            logger_main.error(f"Ошибка при подготовке OHLCV: {str(e)}")
            log_exception(f"Ошибка при подготовке OHLCV: {str(e)}", e)
            return None

    def _prepare_trades(self, trades_df, symbol):
        """Подготавливает данные о сделках"""
        logger_main.debug(f"Подготовка данных о сделках для {symbol}")
        try:
            if trades_df.empty:
                logger_main.warning("Данные о сделках пусты")
                return pd.DataFrame()

            # Фильтруем сделки по символу
            trades_df = trades_df[trades_df['symbol'] == symbol].copy()
            logger_main.debug(f"Количество сделок для {symbol}: {len(trades_df)}")
            if trades_df.empty:
                logger_main.debug(f"Нет сделок для {symbol}")
                return pd.DataFrame()

            # Преобразуем timestamp
            trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'], errors='coerce')
            trades_df = trades_df.dropna(subset=['timestamp'])
            logger_main.debug(f"Количество сделок после преобразования timestamp: {len(trades_df)}")
            if trades_df.empty:
                logger_main.warning(f"Все значения timestamp для {symbol} некорректны")
                return pd.DataFrame()

            # Рассчитываем агрегированные метрики (уменьшаем интервал до 1 часа)
            trades_df['pnl_positive'] = (trades_df['pnl'] > 0).astype(int)
            agg_metrics = trades_df.groupby(pd.Grouper(key='timestamp', freq='1H')).agg({
                'pnl': 'mean',
                'pnl_positive': 'mean',  # Доля прибыльных сделок
                'amount': 'sum'  # Общий объём торгов
            }).reset_index()
            logger_main.debug(f"Агрегированные метрики для {symbol}: {len(agg_metrics)} записей")

            return agg_metrics
        except Exception as e:
            logger_main.error(f"Ошибка при подготовке сделок для {symbol}: {str(e)}")
            log_exception(f"Ошибка при подготовке сделок: {str(e)}", e)
            return None

    def _combine_data(self, ohlcv_df, trades_df):
        """Объединяет OHLCV и данные о сделках"""
        logger_main.debug("Объединение OHLCV и данных о сделках")
        try:
            if ohlcv_df.empty:
                logger_main.warning("OHLCV данные пусты")
                return None
            if trades_df is None:
                logger_main.warning("Данные о сделках не подготовлены")
                return None
            if trades_df.empty:
                logger_main.debug("Данные о сделках пусты, возвращаем только OHLCV")
                return ohlcv_df

            # Сбрасываем индекс, чтобы timestamp стал столбцом
            ohlcv_df = ohlcv_df.reset_index()
            logger_main.debug(f"OHLCV после сброса индекса: {ohlcv_df.columns}")

            # Приводим временные метки к ближайшему 4-часовому интервалу
            ohlcv_df['timestamp'] = ohlcv_df['timestamp'].dt.floor('4H')

            # Объединяем данные
            combined = ohlcv_df.merge(trades_df, on='timestamp', how='left')
            logger_main.debug(f"Длина объединённых данных: {len(combined)}")

            # Заполняем пропуски
            combined['pnl'] = combined['pnl'].fillna(0)
            combined['pnl_positive'] = combined['pnl_positive'].fillna(0)
            combined['amount'] = combined['amount'].fillna(0)

            return combined
        except Exception as e:
            logger_main.error(f"Ошибка при объединении данных: {str(e)}")
            log_exception(f"Ошибка при объединении данных: {str(e)}", e)
            return None

ml_data_preprocessor = MLDataPreprocessor()
__all__ = ['ml_data_preprocessor']
