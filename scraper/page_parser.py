from bs4 import BeautifulSoup


class PageParser:
    """Parses structured HTML content from Similarweb pages and extracts metrics."""

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def parse(self) -> dict:
        """Calls all extraction methods and returns a dictionary of parsed data."""

        return {
            "global_rank": self.extract_global_rank(),
            "total_visits": self.extract_total_visits(),
            "bounce_rate": self.extract_bounce_rate(),
            "pages_per_visit": self.extract_pages_per_visit(),
            "avg_visit_duration": self.extract_avg_visit_duration(),
            "rank_changes": self.extract_rank_changes(),
            "monthly_visits": self.extract_monthly_visits(),
            "last_month_change": self.extract_traffic_change(),
            "top_countries": self.extract_top_countries(),
            "age_distribution": self.extract_age_distribution(),
        }

    def extract_global_rank(self):
        return None

    def extract_total_visits(self):
        return None

    def extract_bounce_rate(self):
        return None

    def extract_pages_per_visit(self):
        return None

    def extract_avg_visit_duration(self):
        return None

    def extract_rank_changes(self):
        return None

    def extract_monthly_visits(self):
        return None

    def extract_traffic_change(self):
        return None

    def extract_top_countries(self):
        return None

    def extract_age_distribution(self):
        return None


if __name__ == "__main__":
    import os
    from pprint import pprint

    print("Working directory:", os.getcwd())

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_html_dir = os.path.join(ROOT_DIR, "data", "raw_html")

    # Get all HTML files in the folder
    html_filenames = []
    for f in os.listdir(raw_html_dir):
        if f.endswith(".html"):
            html_filenames.append(f)

    if not html_filenames:
        raise FileNotFoundError("No HTML files found in data/raw_html/")

    # Pick the first one
    sample_path = os.path.join(raw_html_dir, html_filenames[0])

    with open(sample_path, "r", encoding="utf-8") as f:
        html = f.read()

    # parser = PageParser(html)
    # result = parser.parse()

    pprint(html)
