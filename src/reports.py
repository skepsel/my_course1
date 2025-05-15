import functools
from typing import Optional

import pandas as pd

from src.utils import filter_transactions_by_month


def save_to_jsonl(filename: str):
    """
    Декоратор для записи возвращаемых данных функции в файл в формате jsonl.

    Args:
        filename (str): Путь к файлу для записи данных
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            result.to_json(filename, orient="records", lines=True, force_ascii=False)
            return result

        return wrapper

    return decorator


DAYS_RU = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
    6: "воскресенье",
}


@save_to_jsonl("data/reports.jsonl")
def calculate_average_spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция принимает DataFrame и дату (если не передается — берет текущую дату),
    считает средние траты за день недели за последние три месяца от указанной даты,
    и возвращает DataFrame с колонками 'Дата платежа', 'Средняя трата', 'День недели'.

    Args:
        transactions (pd.DataFrame): Данные о транзакциях.
        date (Optional[str]): Дата в формате "%Y-%m-%d %H:%M:%S" для фильтрации (по умолчанию — сегодняшняя дата).

    Returns:
        pd.DataFrame: DataFrame с тремя колонками: 'Дата платежа', 'День недели', 'Средняя трата'.
    """
    filtered_data = filter_transactions_by_month(transactions, date)
    result = (
        filtered_data.groupby("Дата платежа", as_index=False)["Сумма операции с округлением"]
        .mean()
        .rename(columns={"Сумма операции с округлением": "Средняя трата"})
    )
    result["Дата платежа"] = pd.to_datetime(result["Дата платежа"], errors="coerce", dayfirst=True)
    result["Дата платежа"] = result["Дата платежа"].dt.strftime("%Y-%m-%d")
    result["Средняя трата"] = result["Средняя трата"].round(2)
    result["День недели"] = result["Дата платежа"].apply(lambda x: DAYS_RU[pd.to_datetime(x).weekday()])
    result = result[["Дата платежа", "День недели", "Средняя трата"]]
    return result.iloc[::-1].reset_index(drop=True)
