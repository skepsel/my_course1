import re


def filter_transactions_by_category_or_description(list_tran: list[dict], str_search: str) -> list[dict]:
    """
    Функция для поиска всех транзакций с введенной категорией или описанием
    """
    pattern = re.compile(str_search, re.IGNORECASE)
    operations = [
        op
        for op in list_tran
        if pattern.search(str(op.get("category", "")))  # lowercase ключ
        or pattern.search(str(op.get("description", "")))  # lowercase ключ
    ]
    return operations
