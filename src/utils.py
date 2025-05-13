import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)

load_dotenv()
API_KEY_CUR_USD = os.getenv("API_KEY_CUR_USD")
API_KEY_POS = os.getenv("API_KEY_STOCK")

try:
    df = pd.read_excel("data/operations.xlsx")
    operations_df = df.to_dict(orient="records")
except FileNotFoundError:
    logging.error("Файл operations.xlsx не найден.")
    operations_df = []


def get_month_date_range(date: str) -> Tuple[str, str]:
    """
    Возвращает начальную и конечную даты для заданного месяца.

    Args:
        date (str): Дата в формате "%Y-%m-%d %H:%M:%S".

    Returns:
        Tuple[str, str]: Начальная и конечная даты месяца в формате "%d.%m.%Y".
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        start_of_month = date_obj.replace(day=1)
        return start_of_month.strftime("%d.%m.%Y"), date_obj.strftime("%d.%m.%Y")
    except ValueError:
        logging.error("Неверный формат даты.")
        return "", ""


def filter_operations_by_date(time: str) -> List[Dict]:
    """
    Фильтрует операции по заданному временному диапазону.

    Args:
        time (str): Временная метка в формате "%Y-%m-%d %H:%M:%S".

    Returns:
        List[Dict]: Список операций, отфильтрованных по временному диапазону.
    """
    start_date, end_date = get_month_date_range(time)
    if not start_date or not end_date:
        return []

    start_date = pd.to_datetime(start_date, dayfirst=True)
    end_date = pd.to_datetime(end_date, dayfirst=True)
    filtered_operations = [
        op
        for op in operations_df
        if start_date <= pd.to_datetime(op["Дата операции"], dayfirst=True) <= end_date
    ]
    return filtered_operations


def get_time_of_day_greeting() -> str:
    """
    Возвращает приветствие в зависимости от текущего времени суток.

    Returns:
        str: Приветствие ("Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи").
    """
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def extract_operation_details(operations: List[Dict]) -> Tuple[List, List, List]:
    """
    Извлекает информацию о картах, суммах операций и кэшбэке из списка операций.

    Args:
        operations (List[Dict]): Список операций.

    Returns:
        Tuple[List, List, List]: Кортеж списков с номерами карт, суммами операций и кэшбэком.
    """
    card_numbers = [op.get("Номер карты", "Неизвестно") for op in operations]
    transaction_amounts = [
        op.get("Сумма операции с округлением", 0) for op in operations
    ]
    cashback_values = [op.get("Кэшбэк", 0) for op in operations]
    return card_numbers, transaction_amounts, cashback_values


def get_top_transactions(operations: List[Dict]) -> List[Dict]:
    """
    Возвращает топ-5 транзакций по сумме операции.

    Args:
        operations (List[Dict]): Список операций.

    Returns:
        List[Dict]: Список топ-5 транзакций.
    """
    return sorted(
        operations, key=lambda x: x["Сумма операции с округлением"], reverse=True
    )[:5]


def fetch_currency_and_stock_data(user_settings: str) -> Tuple[List, List]:
    """
    Получает курсы валют и стоимость акций на основе пользовательских настроек.

    Args:
        user_settings (str): Путь к файлу с пользовательскими настройками.

    Returns:
        Tuple[List, List]: Кортеж списков с информацией о курсах валют и акциях.
    """
    currency_data = []
    stock_data = []
    try:
        with open(user_settings, encoding="utf-8") as file:
            settings = json.load(file)
    except FileNotFoundError:
        logging.error("Файл настроек не найден.")
        return currency_data, stock_data

    currencies = ",".join(settings.get("user_currencies", []))
    currency_url = f"http://api.currencylayer.com/live?access_key={API_KEY_CUR_USD}&currencies={currencies}"

    try:
        response_currency = requests.get(currency_url)
        response_currency.raise_for_status()
        data_currency = response_currency.json()
        if "quotes" in data_currency:
            for currency in settings.get("user_currencies", []):
                key = f"{currency}RUB"
                if key in data_currency["quotes"]:
                    currency_data.append(
                        {
                            "currency": currency,
                            "rate": round(data_currency["quotes"][key], 2),
                        }
                    )
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе курсов валют: {e}")

    stocks = ",".join(settings.get("user_stocks", []))
    stock_url = f"http://api.marketstack.com/v1/eod/latest?access_key={API_KEY_POS}&symbols={stocks}"

    try:
        response_stocks = requests.get(stock_url)
        response_stocks.raise_for_status()
        data_stocks = response_stocks.json()
        if "data" in data_stocks:
            for stock in data_stocks["data"]:
                stock_data.append(
                    {"stock": stock["symbol"], "price": float(stock["close"])}
                )
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе акций: {e}")

    return currency_data, stock_data


def filter_transactions_by_month(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:
    """
    Фильтрует транзакции за последние три месяца от заданной даты.

    Args:
        transactions (pd.DataFrame): DataFrame с транзакциями.
        date (Optional[str]): Дата в формате "%Y-%m-%d %H:%M:%S". По умолчанию текущая дата.

    Returns:
        pd.DataFrame: Отфильтрованный DataFrame с транзакциями.
    """
    if date is None:
        date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    try:
        end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        start_date = end_date - timedelta(days=90)
    except ValueError:
        logging.error("Неверный формат даты.")
        return pd.DataFrame()

    transactions["Дата платежа"] = pd.to_datetime(
        transactions["Дата платежа"], errors="coerce", dayfirst=True
    )

    filtered_transactions = transactions[
        (transactions["Дата платежа"] >= start_date)
        & (transactions["Дата платежа"] <= end_date)
    ]

    return filtered_transactions
