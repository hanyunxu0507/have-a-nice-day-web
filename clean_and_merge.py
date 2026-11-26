"""Clean order/customer CSV files, convert amounts to CNY, merge, and export to SQLite."""

import argparse
import csv
import sqlite3
from pathlib import Path

RATES = {"USD": 6.9, "EUR": 7.5, "CNY": 1.0, "JPY": 0.05}
BASE_DIR = Path(__file__).resolve().parent


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def clean_rows(rows: list[dict[str, str]], key: str) -> list[dict[str, str]]:
    """Remove exact duplicate rows and repeated key values, keeping the first row."""
    seen_rows: set[tuple] = set()
    seen_keys: set[str] = set()
    cleaned: list[dict[str, str]] = []

    for row in rows:
        signature = tuple(sorted(row.items()))
        if signature in seen_rows:
            continue
        seen_rows.add(signature)

        if key in row:
            if row[key] in seen_keys:
                continue
            seen_keys.add(row[key])

        cleaned.append(row)

    return cleaned


def convert_to_cny(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    converted: list[dict[str, str]] = []

    for row in rows:
        item = dict(row)
        currency = item["currency"].strip().upper()
        if currency not in RATES:
            raise ValueError(f"Unsupported currency: {currency}")

        amount = float(item["amount"].replace(",", "").strip())
        item["currency"] = currency
        item["amount"] = amount
        item["amount_cny"] = round(amount * RATES[currency], 2)
        converted.append(item)

    return converted


def merge_data(
    orders: list[dict[str, str]], customers: list[dict[str, str]]
) -> list[dict[str, object]]:
    customers_by_id = {row["customer_id"]: row for row in customers}
    merged: list[dict[str, object]] = []

    for order in orders:
        customer = customers_by_id.get(order["customer_id"])
        if customer is None:
            continue

        merged.append(
            {
                "order_id": order["order_id"],
                "customer_id": order["customer_id"],
                "order_date": order["order_date"],
                "amount": order["amount"],
                "currency": order["currency"],
                "amount_cny": order["amount_cny"],
                "customer_name": customer["customer_name"],
                "region": customer["region"],
            }
        )

    return merged


def write_database(merged: list[dict[str, object]], db_path: Path) -> None:
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("DROP TABLE IF EXISTS merged_orders")
        connection.execute(
            """
            CREATE TABLE merged_orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                order_date TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                amount_cny REAL NOT NULL,
                customer_name TEXT,
                region TEXT
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO merged_orders (
                order_id, customer_id, order_date, amount, currency,
                amount_cny, customer_name, region
            ) VALUES (
                :order_id, :customer_id, :order_date, :amount, :currency,
                :amount_cny, :customer_name, :region
            )
            """,
            merged,
        )

        connection.execute("DROP TABLE IF EXISTS region_summary")
        connection.execute(
            """
            CREATE TABLE region_summary AS
            SELECT
                region,
                ROUND(AVG(amount_cny), 2) AS average_amount_cny,
                COUNT(*) AS order_count
            FROM merged_orders
            GROUP BY region
            ORDER BY region
            """
        )
        connection.commit()

        print(f"Merged rows: {len(merged)}")
        print("region_summary:")
        for row in connection.execute("SELECT * FROM region_summary"):
            print(row)
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=Path, default=BASE_DIR / "data" / "orders.csv")
    parser.add_argument("--customers", type=Path, default=BASE_DIR / "data" / "customers.csv")
    parser.add_argument("--database", type=Path, default=BASE_DIR / "merged_data.db")
    args = parser.parse_args()

    orders = clean_rows(read_csv(args.orders), key="order_id")
    customers = clean_rows(read_csv(args.customers), key="customer_id")

    orders = convert_to_cny(orders)
    merged = merge_data(orders, customers)

    write_database(merged, args.database)
    print(f"Database written to: {args.database}")


if __name__ == "__main__":
    main()
