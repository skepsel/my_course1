import pytest


@pytest.fixture
def sample_transactions_data():
    """
    Фикстура для создания тестовых данных транзакций.

    Возвращает список словарей, представляющих транзакции с категориями,
    суммами и датами. Эти данные будут использоваться в тестах.

    Returns:
        list[dict]: Список тестовых транзакций.
    """
    return [
        {"category": "food", "amount": 100, "date": "2018-04-01 00:00:00"},
        {"category": "transport", "amount": 50, "date": "2018-04-01 00:00:00"},
    ]
