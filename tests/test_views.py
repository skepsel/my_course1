import json
from unittest.mock import patch

import pytest

from src.views import generate_filtered_json


@pytest.fixture
def mock_dependencies():
    with (
        patch("src.views.generate_filtered_json") as mock_filtered,
        patch("src.views.get_time_of_day_greeting") as mock_greet,
        patch("src.views.extract_operation_details") as mock_info,
        patch("src.views.get_top_transactions") as mock_top5,
        patch("src.views.fetch_currency_and_stock_data") as mock_rates,
    ):
        mock_filtered.return_value = [
            {
                "Номер карты": "1234567890123456",
                "Сумма операции с округлением": 150.75,
                "Кэшбэк": 5.25,
                "Дата платежа": "2023-05-15",
                "Категория": "Рестораны",
                "Описание": "Поход в кафе",
            }
        ]
        mock_greet.return_value = "Доброе утро"
        mock_info.return_value = (["1234567890123456"], [150.75], [5.25])
        mock_top5.return_value = mock_filtered.return_value
        mock_rates.return_value = (
            [{"currency": "USD", "rate": 95.5}],
            [{"stock": "AAPL", "price": 172.5}],
        )

        yield


def test_write_json_gl(mock_dependencies):
    result = generate_filtered_json("2023-05-20 10:00:00")
    result_dict = json.loads(result)

    # Проверяем, что ключи присутствуют в результирующем словаре
    assert "greeting" in result_dict
    assert "cards" in result_dict
    assert "top_transactions" in result_dict
    assert "currency_rates" in result_dict
    assert "stock_prices" in result_dict

    # Проверяем значения в каждом из разделов
    assert result_dict["greeting"] == "Доброе утро"

    # Проверяем содержимое карты
    assert len(result_dict["cards"]) == 1
    card = result_dict["cards"][0]
    assert card["last_digits"] == "3456"
    assert card["total_spent"] == 150.75
    assert card["cashback"] == 5.25

    # Проверяем топ транзакций
    assert len(result_dict["top_transactions"]) == 1
    top_transaction = result_dict["top_transactions"][0]
    assert top_transaction["category"] == "Рестораны"

    # Проверяем курсы валют и цены на акции
    assert len(result_dict["currency_rates"]) == 1
    assert result_dict["currency_rates"][0]["currency"] == "USD"
    assert result_dict["currency_rates"][0]["rate"] == 95.5

    assert len(result_dict["stock_prices"]) == 1
    assert result_dict["stock_prices"][0]["stock"] == "AAPL"
    assert result_dict["stock_prices"][0]["price"] == 172.5

    # Дополнительная проверка на тип данных результата
    assert isinstance(result, str), f"Expected result to be a string, but got {type(result)}"
    assert isinstance(result_dict, dict), f"Expected result_dict to be a dict, but got {type(result_dict)}"
