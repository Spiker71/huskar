import logging
import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
from PIL import ImageGrab
import datetime
import time
import subprocess
import sys
import os
import ta

# Функция для установки необходимых пакетов
def install_packages():
    packages = ['numpy', 'matplotlib', 'python-binance', 'ta', 'Pillow']
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            logging.error(f"Failed to install package {package}: {e}")

# Установка пакетов
install_packages()

# Вставьте ваш API ключ и секрет сюда
api_key = 'czs8NPf9uo1va2Sg4HB5NCWFO7XGNtP8RPHWLWU8eWqNw0XhqjCsPhJreJfaEMhv'
api_secret = 'v0Onk3jFT4G5Q4vufMt3eDqT2r2cKKW4NoOQC53uLNSfjRcBHfqdmYBrHaFa3Udx'

# Создание клиента Binance
client = Client(api_key, api_secret)

def get_historical_klines(symbol, interval, start_str):
    """Получение исторических данных"""
    klines = client.get_historical_klines(symbol, interval, start_str)
    return klines

def calculate_fibonacci_levels(data):
    """Расчет уровней Фибоначчи"""
    max_price = max(data)
    min_price = min(data)
    diff = max_price - min_price
    levels = {
        '0.0%': max_price,
        '23.6%': max_price - 0.236 * diff,
        '38.2%': max_price - 0.382 * diff,
        '50.0%': max_price - 0.5 * diff,
        '61.8%': max_price - 0.618 * diff,
        '100.0%': min_price
    }
    return levels

def find_trade_signals(data, levels):
    """Поиск точек входа на основе уровней Фибоначчи"""
    signals = []
    for i in range(1, len(data)):
        if data[i-1] > levels['38.2%'] and data[i] <= levels['38.2%']:
            signals.append(('Buy', i))
        elif data[i-1] < levels['61.8%'] and data[i] >= levels['61.8%']:
            signals.append(('Sell', i))
    return signals

def add_indicators(data):
    """Добавление индикаторов"""
    data['rsi'] = ta.momentum.RSIIndicator(close=data['close']).rsi()
    return data

def analyze_market():
    """Основная функция для анализа рынка"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']  # добавьте сюда нужные вам символы
    intervals = [Client.KLINE_INTERVAL_15MINUTE, Client.KLINE_INTERVAL_1HOUR]

    for symbol in symbols:
        for interval in intervals:
            start_str = '1 month ago UTC'

            # Получение исторических данных
            klines = get_historical_klines(symbol, interval, start_str)
            close_prices = np.array([float(kline[4]) for kline in klines])
            
            # Пример: добавление индикаторов
            data = {'close': close_prices}
            data = add_indicators(data)

            # Рассчет уровней Фибоначчи
            fibonacci_levels = calculate_fibonacci_levels(close_prices)

            # Поиск точек входа
            signals = find_trade_signals(close_prices, fibonacci_levels)

            # Логирование сигналов
            for signal in signals:
                logging.info(f"Signal: {signal[0]} at index {signal[1]} (price: {close_prices[signal[1]]}) for {symbol} on {interval}")
            
            # Сохранение графиков с уровнями Фибоначчи и сигналами
            save_chart(symbol, interval, close_prices, fibonacci_levels, signals
