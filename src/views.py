import json
from collections import defaultdict

import pandas as pd

from src.utils import (
    extract_operation_details,
    fetch_currency_and_stock_data,
    filter_operations_by_date,
    get_time_of_day_greeting,
    get_top_transactions,
)


def generate_filtered_json(time_setting: str) -> str:
    """
    Возвращает JSON с отфильтрованными транзакциями от введенной даты до начала месяца
    с информацией о картах (траты, кэшбек), топ-5 транзакций и курсах валют и акций.

    Args:
        time_setting (str): Временная метка в формате "%Y-%m-%d %H:%M:%S".

    Returns:
        str: JSON с результатами.
    """
    # Получаем данные
    operations = filter_operations_by_date(time_setting)
    greeting_message = get_time_of_day_greeting()
    card_numbers, amounts, cashback = extract_operation_details(operations)
    top_transactions = get_top_transactions(operations)
    currency_data, stock_data = fetch_currency_and_stock_data("user_settings.json")

    # Подготовка данных по картам
    card_data = defaultdict(lambda: {"total_spent": 0, "cashback": 0})

    for card, amount, cash in zip(card_numbers, amounts, cashback):
        last_digits = card[-4:] if pd.notna(card) and len(str(card)) >= 4 else "----"
        card_data[last_digits]["total_spent"] += amount if pd.notna(amount) else 0
        card_data[last_digits]["cashback"] += cash if pd.notna(cash) else 0

    # Составляем информацию по картам
    cards_info = [
        {
            "last_digits": card,
            "total_spent": round(data["total_spent"], 2),
            "cashback": round(data["cashback"], 2),
        }
        for card, data in card_data.items()
    ]

    # Составляем информацию по топ-5 транзакциям
    top_transactions_info = [
        {
            "date": op.get("Дата платежа", ""),
            "amount": op.get("Сумма операции с округлением", 0),
            "category": op.get("Категория", ""),
            "description": op.get("Описание", ""),
        }
        for op in top_transactions
    ]

    # Создаем итоговый JSON
    information_json = {
        "greeting": greeting_message,
        "cards": cards_info,
        "top_transactions": top_transactions_info,
        "currency_rates": currency_data,
        "stock_prices": stock_data,
    }

    return json.dumps(information_json, ensure_ascii=False, indent=4)
