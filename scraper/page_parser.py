from bs4 import BeautifulSoup
from typing import Optional


class PageParser:
    """Parses structured HTML content from Similarweb pages and extracts metrics."""

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def extract_from_nested(self, parent_selector: str, child_selector: str) -> Optional[str]:
        """ For standard div > p lookups"""
        parent = self.soup.select_one(parent_selector)
        if parent:
            child = parent.select_one(child_selector)
            if child and child.text:
                return child.text.strip()
        return None

    def extract_from_nested_by_attribute(
            self,
            container_selector: str,
            label_tag: str,
            label_attr: str,
            label_value: str,
            value_selector: str
    ) -> Optional[str]:
        """ For filtering by attribute"""
        containers = self.soup.select(container_selector)
        for container in containers:
            label = container.select_one(f"{label_tag}[{label_attr}='{label_value}']")
            if label:
                value = container.select_one(value_selector)
                if value and value.text:
                    return value.text.strip()
        return None

    def extract_from_nested_by_label_text(
            self,
            container_selector: str,
            label_tag: str,
            label_text: str,
            value_selector: str
    ) -> Optional[str]:
        """Extracts a value based on a label's text inside a container."""
        containers = self.soup.select(container_selector)
        for container in containers:
            label = container.select_one(label_tag)
            if label and label.text.strip().lower() == label_text.lower():
                value = container.select_one(value_selector)
                if value and value.text:
                    return value.text.strip()
        return None


if __name__ == "__main__":
    import os
    from pprint import pprint

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_html_dir = os.path.join(ROOT_DIR, "data", "raw_html")

    # Get all HTML files in the folder
    html_filenames = []
    for f in os.listdir(raw_html_dir):
        if f.endswith(".html"):
            html_filenames.append(f)

    if not html_filenames:
        raise FileNotFoundError("No HTML files found in data/raw_html/")

    # Pick the file
    sample_path = os.path.join(raw_html_dir, html_filenames[1])

    with open(sample_path, "r", encoding="utf-8") as f:
        html = f.read()

    print(f"Parsing file: {html_filenames[1]}")
    # pprint(html)

    parser = PageParser(html)

    extract_global_rank = parser.extract_from_nested(
        parent_selector="div.wa-rank-list__item.wa-rank-list__item--global",
        child_selector="p.wa-rank-list__value")

    extract_total_visits = parser.extract_from_nested(
        parent_selector="div.wa-overview__column.wa-overview__column--engagement",
        child_selector="p.engagement-list__item-value")

    extract_bounce_rate = parser.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="bounce-rate",
        value_selector="p.engagement-list__item-value")

    extract_pages_per_visit = parser.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="pages-per-visit",
        value_selector="p.engagement-list__item-value")

    extract_avg_visit_duration = parser.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="avg-visit-duration",
        value_selector="p.engagement-list__item-value")

    extract_rank_changes = parser.extract_from_nested_by_label_text(
        container_selector="div.wa-traffic__engagement-item",
        label_tag="span.wa-traffic__engagement-item-title",
        label_text="Last Month Change",
        value_selector="span.wa-traffic__engagement-item-value")

    extract_monthly_visits = ""
    extract_traffic_change = ""
    extract_top_countries = ""
    extract_age_distribution = ""

    print("global_rank: ", extract_global_rank)
    print("total_visits: ", extract_total_visits)
    print("bounce_rate: ", extract_bounce_rate)
    print("pages_per_visit: ", extract_pages_per_visit)
    print("avg_visit_duration: ", extract_avg_visit_duration)
    print("rank_changes: ", extract_rank_changes)
    print("monthly_visits: ", extract_monthly_visits)
    print("last_month_change: ", extract_traffic_change)
    print("top_countries: ", extract_top_countries)
    print("age_distribution: ", extract_age_distribution)
