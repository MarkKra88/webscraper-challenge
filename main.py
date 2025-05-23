import os
import pandas as pd
from datetime import datetime
from etl.extract_and_transform import extract_and_transform
from etl.load_to_db import DatabaseLoader


def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Data saved to {output_path}")


def main():
    print("Starting Extract and Transform phase...")
    df = extract_and_transform()

    if df.empty:
        print("No data extracted. Skipping Load phase.")
        return

    print("\nChoose etl option:")
    print("1. Save to CSV")
    print("2. Load to SQLite")
    print("3. Both")
    print("4. Exit")

    choice = input("Enter choice [1-5]: ").strip()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = os.path.join("data", "output","csv", f"data_{timestamp}.csv")
    sqlite_db = os.path.join("data", "output", "sqlite", "web_metrics.sqlite")

    if choice == "1":
        save_to_csv(df, output_csv)
    elif choice == "2":
        loader = DatabaseLoader(df)
        loader.load_to_sqlite(sqlite_db)
    elif choice == "3":
        save_to_csv(df, output_csv)
        loader = DatabaseLoader(df)
        loader.load_to_sqlite(sqlite_db)
    else:
        pass


if __name__ == "__main__":
    main()