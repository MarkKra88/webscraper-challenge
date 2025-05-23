import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# Create the output directory for graphs
GRAPH_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "output", "graphs")
os.makedirs(GRAPH_DIR, exist_ok=True)


def parse_json_column(column):
    if isinstance(column, str):
        try:
            return json.loads(column.replace("'", '"'))
        except Exception:
            return []
    return column


def compute_growth(series):
    growth = []
    for i in range(1, len(series)):
        prev = series[i - 1]
        curr = series[i]
        if prev and curr and prev != 0:
            growth.append(round(((curr - prev) / prev) * 100, 2))
        else:
            growth.append(None)
    return growth


def analyze_metrics(df):
    df['monthly_visits'] = df['monthly_visits'].apply(parse_json_column)
    df['rank_changes'] = df['rank_changes'].apply(parse_json_column)

    site_growth = []
    for _, row in df.iterrows():
        filename = row['filename']

        # VISITS GROWTH
        months = []
        visits = []
        for v in row['monthly_visits']:
            if isinstance(v, dict) and 'visits' in v and 'month' in v:
                months.append(v['month'])
                visits.append(v['visits'])

        visit_growth = compute_growth(visits)

        if visit_growth:
            plt.figure()
            plt.plot(months[1:], visit_growth, marker='o')
            plt.title(f"Month-on-Month Growth in Visits ({filename})")
            plt.xlabel("Month")
            plt.ylabel("Growth (%)")
            plt.grid(True)
            plt.savefig(os.path.join(GRAPH_DIR, f"visits_growth_{filename.replace('.html', '')}.png"))
            plt.close()

        # RANK GROWTH

        months = []
        ranks = []
        for v in row['rank_changes']:
            if isinstance(v, dict) and 'rank' in v and 'month' in v:
                months.append(v['month'])
                ranks.append(v['rank'])

        rank_growth = compute_growth(ranks)

        if rank_growth:
            plt.figure()
            plt.plot(months[1:], rank_growth, marker='o', color='orange')
            plt.title(f"Month-on-Month Growth in Rank ({filename})")
            plt.xlabel("Month")
            plt.ylabel("Growth (%)")
            plt.grid(True)
            plt.savefig(os.path.join(GRAPH_DIR, f"rank_growth_{filename.replace('.html', '')}.png"))
            plt.close()

        # Store average growth for comparison
        avg_visit = sum(v for v in visit_growth if v is not None) / len(visit_growth) if visit_growth else 0
        avg_rank = sum(v for v in rank_growth if v is not None) / len(rank_growth) if rank_growth else 0
        score = avg_visit - avg_rank  # Better if visits up and rank down
        site_growth.append({"site": filename, "score": round(score, 2)})

    # RELATIVE RANKING
    site_growth = sorted(site_growth, key=lambda x: x['score'], reverse=True)
    sites = [x['site'] for x in site_growth]
    scores = [x['score'] for x in site_growth]

    if site_growth:
        plt.figure(figsize=(10, 6))
        plt.barh(sites, scores, color='green')
        plt.xlabel("Relative Growth Score")
        plt.title("Site Ranking by Combined Growth (Visits ↑ and Rank ↓)")
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPH_DIR, "relative_growth_ranking.png"))
        plt.close()


if __name__ == "__main__":
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(ROOT_DIR, "data", "output", "sqlite", "web_metrics.sqlite")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"SQLite DB not found at {db_path}")

    # Load full table from SQLite
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM web_metrics", conn)
    conn.close()

    analyze_metrics(df)
    print("Graphs saved to:", GRAPH_DIR)
