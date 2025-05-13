import pytest

from src.services import filter_transactions_by_category_or_description


@pytest.fixture
def valid_data():
    """
    Фикстура для предоставления тестовых данных транзакций.

    Returns:
        list[dict]: Список транзакций с категориями и суммами.
    """
    return [{"category": "еда", "amount": 100}, {"category": "транспорт", "amount": 50}]


def test_filter_transactions_by_category_or_description(valid_data):
    """
    Тестирование функции filter_transactions_by_category_or_description.

    Проверяет, что функция корректно фильтрует транзакции по поисковому термину.

    Args:
        valid_data (list[dict]): Список тестовых данных транзакций.
    """
    result = filter_transactions_by_category_or_description(valid_data, "еда")

    # Проверяем, что результат является списком
    assert isinstance(
        result, list
    ), f"Функция должна возвращать список, но получен {type(result)}"

    # Проверяем, что результат содержит транзакцию с категорией "еда"
    assert any(
        transaction["category"] == "еда" for transaction in result
    ), "Результат должен содержать транзакцию с категорией 'еда'"

    # Проверяем, что результат не пустой
    assert result, "Результат должен содержать хотя бы одну транзакцию"
