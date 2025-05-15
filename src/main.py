import pandas as pd

from src.reports import calculate_average_spending_by_weekday
from src.services import filter_transactions_by_category_or_description
from src.views import generate_filtered_json

df = pd.read_excel("data/operations.xlsx")
operations_df = df.to_dict(orient="records")


def main():
    json_output = generate_filtered_json("2018-05-28 00:00:00")
    found_transactions = filter_transactions_by_category_or_description(operations_df, "Рестораны")
    weekday_spending = calculate_average_spending_by_weekday(df, "2018-05-18 00:00:00")

    print("=== JSON Report ===")
    print(json_output)

    print("\n=== Найденные транзакции по категории 'Рестораны' ===")
    for item in found_transactions:
        print(item)

    print("\n=== Средние траты по дням недели ===")
    print(weekday_spending.to_string(index=False))


if __name__ == "__main__":
    main()
