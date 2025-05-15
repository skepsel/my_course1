import pandas as pd
import pytest

from src.reports import calculate_average_spending_by_weekday

# Загрузка данных из Excel
df = pd.read_excel("data/operations.xlsx")


@pytest.fixture
def valid_datetime():
    """
    Фикстура для предоставления действительной временной метки.

    Returns:
        str: Действительная временная метка в формате "%Y-%m-%d %H:%M:%S".
    """
    return "2018-04-04 12:00:00"


def test_calculate_average_spending_by_weekday(valid_datetime):
    """
    Тестирование функции calculate_average_spending_by_weekday.

    Проверяет, что функция возвращает правильный тип данных (DataFrame)
    и что полученный DataFrame не пустой.

    Args:
        valid_datetime (str): Временная метка для теста.
    """
    result = calculate_average_spending_by_weekday(df, valid_datetime)

    # Проверяем, что результат является DataFrame
    assert isinstance(result, pd.DataFrame), f"Функция должна возвращать DataFrame, но получен {type(result)}"

    # Проверяем, что DataFrame не пустой
    assert not result.empty, "DataFrame не должен быть пустым"
