import os
import sqlite3
import pandas as pd
import json
import sys


class DatabaseLoader:

    """Handles transformation and loading of web metrics data into a SQLite database."""
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def _prepare_data(self):
        """
        Convert list or dictionary columns to JSON strings.
        """

        for col in self.df.columns:
            if self.df[col].apply(lambda v: isinstance(v, (list, dict))).any():
                self.df[col] = self.df[col].apply(json.dumps)

    def load_to_sqlite(self, db_path: str, table_name: str = "web_metrics"):

        self._prepare_data()

        dtype_map = {
            "filename": "TEXT",
            "global_rank": "INTEGER",
            "total_visits": "INTEGER",
            "bounce_rate": "REAL",
            "pages_per_visit": "REAL",
            "avg_visit_duration": "INTEGER",
            "last_month_change": "REAL",
            "rank_changes": "TEXT",  # Lists → stored as stringified JSON
            "monthly_visits": "TEXT",
            "top_countries": "TEXT",
            "age_distribution": "TEXT",
            "status": "TEXT",
            "missing_fields": "TEXT"
        }

        with sqlite3.connect(db_path) as conn:
            self.df.to_sql(
                name=table_name,
                con=conn,
                if_exists="replace",
                index=False,
                dtype=dtype_map
            )

        print(f"Data successfully written to {db_path} in table '{table_name}'.")


if __name__ == "__main__":
    """
    Allows the script to be run directly to load a selected CSV file into SQLite,
    then prints sample schema and data.
    """

    from pprint import pprint
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(ROOT_DIR, "data", "output", "csv")
    print(output_dir)
    db_path = os.path.join(ROOT_DIR, "data", "output", "sqlite", "web_metrics.sqlite")
    print(db_path)

    # Traditional loop to gather CSV files
    csv_files = []
    for f in os.listdir(output_dir):
        if f.endswith(".csv"):
            csv_files.append(f)

    if not csv_files:
        print("No CSV files found in data/output/csv")
        sys.exit()

    print("Available CSV files:")
    for filename in csv_files:
        print("-", filename)

    selected_filename = input("\nEnter the exact CSV filename to load into SQLite (case-sensitive): ").strip()

    if selected_filename not in csv_files:
        print(f"'{selected_filename}' not found in data/output/csv.")
        sys.exit()

    csv_path = os.path.join(output_dir, selected_filename)
    df = pd.read_csv(csv_path)

    loader = DatabaseLoader(df)
    loader.load_to_sqlite(db_path)

    print("------- SQLite output -------")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(web_metrics);")
    print("Columns & Types:")
    pprint(cursor.fetchall())

    cursor.execute("SELECT * FROM web_metrics LIMIT 3;")
    print("Sample Data:")
    pprint(cursor.fetchall())
    conn.close()
