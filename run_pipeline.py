import os
import csv
import sys
from pprint import pprint
from scraper.page_parser import PageParser
from utils.normalizer import Normalizer
from utils.error_logger import error_logger


# Ensure local imports work when script is run directly
sys.path.append(os.path.dirname(__file__))


@error_logger
def get_global_rank(page):
    return page.extract_from_nested(
        parent_selector="div.wa-rank-list__item.wa-rank-list__item--global",
        child_selector="p.wa-rank-list__value"
    )


@error_logger
def get_total_visits(page):
    return page.extract_from_nested(
        parent_selector="div.wa-overview__column.wa-overview__column--engagement",
        child_selector="p.engagement-list__item-value"
    )


@error_logger
def get_bounce_rate(page):
    return page.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="bounce-rate",
        value_selector="p.engagement-list__item-value"
    )


@error_logger
def get_pages_per_visit(page):
    return page.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="pages-per-visit",
        value_selector="p.engagement-list__item-value"
    )


@error_logger
def get_avg_visit_duration(page):
    return page.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="avg-visit-duration",
        value_selector="p.engagement-list__item-value"
    )


@error_logger
def get_last_month_change(page):
    return page.extract_from_nested_by_label_text(
        container_selector="div.wa-traffic__engagement-item",
        label_tag="span.wa-traffic__engagement-item-title",
        label_text="Last Month Change",
        value_selector="span.wa-traffic__engagement-item-value"
    )


@error_logger
def get_rank_changes(page):
    return page.extract_line_chart_from_svg_path_auto(
        container_selector="div.wa-ranking__main-content",
        x_label_selector="g.highcharts-axis-labels.highcharts-xaxis-labels text",
        svg_path_selector="g.highcharts-series path.highcharts-graph",
        y_axis_label_selector="g.highcharts-axis-labels.highcharts-yaxis-labels text",
        x_key="month",
        y_key="rank"
    )


@error_logger
def get_monthly_visits(page):
    return page.extract_paired_lists_from_selectors(
        container_selector="div.wa-traffic__chart",
        label_selector="g.highcharts-axis-labels.highcharts-xaxis-labels text",
        value_selector="tspan.wa-traffic__chart-data-label",
        label_key="month",
        value_key="visits"
    )


@error_logger
def get_top_countries(page):
    return page.extract_repeating_labeled_items(
        item_selector="div.wa-geography__country.wa-geography__legend-item",
        label_selector="a.wa-geography__country-name, span.wa-geography__country-name",
        value_selector="span.wa-geography__country-traffic-value"
    )


@error_logger
def get_age_distribution(page):
    return page.extract_paired_lists_from_selectors(
        container_selector="div.wa-demographics__age",
        label_selector="g.highcharts-axis-labels.highcharts-xaxis-labels text",
        value_selector="tspan.wa-demographics__age-data-label",
        label_key="age_group",
        value_key="percentage"
    )


# Define paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
raw_html_dir = os.path.join(ROOT_DIR, "data", "raw_html")
output_csv_path = os.path.join(ROOT_DIR, "data", "output", "data.csv")

# Load HTML files
html_files = [f for f in os.listdir(raw_html_dir) if f.endswith(".html")]
if not html_files:
    raise FileNotFoundError("No HTML files found in data/raw_html/")

records = []

for file in html_files:
    with open(os.path.join(raw_html_dir, file), "r", encoding="utf-8") as f:
        html = f.read()

    parser = PageParser(html)

    raw = {
        "global_rank": get_global_rank(parser),
        "total_visits": get_total_visits(parser),
        "bounce_rate": get_bounce_rate(parser),
        "pages_per_visit": get_pages_per_visit(parser),
        "avg_visit_duration": get_avg_visit_duration(parser),
        "last_month_change": get_last_month_change(parser),
        "rank_changes": get_rank_changes(parser),
        "monthly_visits": get_monthly_visits(parser),
        "top_countries": get_top_countries(parser),
        "age_distribution": get_age_distribution(parser)
    }

    clean = {
        "global_rank": Normalizer.normalize_rank(raw["global_rank"]),
        "total_visits": Normalizer.normalize_number(raw["total_visits"]),
        "bounce_rate": Normalizer.normalize_percentage(raw["bounce_rate"]),
        "pages_per_visit": Normalizer.normalize_number(raw["pages_per_visit"]),
        "avg_visit_duration": Normalizer.normalize_duration(raw["avg_visit_duration"]),
        "last_month_change": Normalizer.normalize_percentage(raw["last_month_change"]),
        "rank_changes": raw["rank_changes"],
        "monthly_visits": raw["monthly_visits"],
        "top_countries": raw["top_countries"],
        "age_distribution": raw["age_distribution"]
    }

    records.append(clean)

pprint(records)

# # Save results
# os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
#
# with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=records[0].keys())
#     writer.writeheader()
#     writer.writerows(records)
#
# print(f"Data saved to {output_csv_path}")
