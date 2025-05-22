from bs4 import BeautifulSoup
from typing import Optional


class PageParser:
    """Parses structured HTML content from Similarweb pages and extracts metrics."""

    def __init__(self, html_content: str, filename: str = "unknown.html"):
        self.soup = BeautifulSoup(html_content, "html.parser")
        self.filename = filename

    def extract_from_nested(self, parent_selector: str, child_selector: str) -> Optional[str]:
        """ For standard div > p lookups"""
        parent = self.soup.select_one(parent_selector)
        if not parent:
            raise ValueError(f"Parent selector not found: {parent_selector}")

        child = parent.select_one(child_selector)
        if not child or not child.text:
            raise ValueError(f"Child selector not found or empty: {child_selector} inside {parent_selector}")

        return child.text.strip()

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
        raise ValueError(f"No matching container found for label attribute: {label_attr}={label_value}")

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
        raise ValueError(f"Label text '{label_text}' not found in container: {container_selector}")

    def extract_repeating_labeled_items(
            self,
            item_selector: str,
            label_selector: str,
            value_selector: str
    ) -> list[dict]:
        """Extracts repeated items with a label and value from a list of blocks."""
        blocks = self.soup.select(item_selector)
        if not blocks:
            raise ValueError(f"No items found for selector: {item_selector}")

        items = []
        for block in blocks:
            label_el = block.select_one(label_selector)
            value_el = block.select_one(value_selector)

            if label_el and value_el:
                items.append({
                    "label": label_el.text.strip(),
                    "value": value_el.text.strip()
                })

        return items

    def extract_paired_lists_from_selectors(
            self,
            container_selector: str,
            label_selector: str,
            value_selector: str,
            label_key: str = "label",
            value_key: str = "value"
    ) -> list[dict]:
        """
        Extracts two lists (labels and values) from a specific container and returns them as paired dictionaries.
        Useful for charts or blocks where items are visually aligned but structurally separated.
        """
        container = self.soup.select_one(container_selector)
        if not container:
            raise ValueError(f"Container not found: {container_selector}")

        labels = [el.text.strip() for el in container.select(label_selector)]
        values = [el.text.strip() for el in container.select(value_selector)]

        if len(labels) != len(values):
            raise ValueError(f"Mismatch: {len(labels)} labels vs {len(values)} values")

        return [
            {label_key: label, value_key: value}
            for label, value in zip(labels, values)
        ]

    def extract_line_chart_from_svg_path_auto(
            self,
            container_selector: str,
            x_label_selector: str,
            svg_path_selector: str,
            y_axis_label_selector: str,
            x_key: str = "label",
            y_key: str = "value"
    ) -> list[dict]:
        """
        Smart extractor for SVG-based line charts.
        Automatically infers pixel-to-value mapping from y-axis labels
        and adjusts for any SVG group 'transform' offset.
        """
        import re

        container = self.soup.select_one(container_selector)
        if not container:
            raise ValueError(f"Container not found: {container_selector}")

        # 1. Parse Y-axis labels and positions
        y_axis_labels = container.select(y_axis_label_selector)
        y_axis_data = []
        for el in y_axis_labels:
            try:
                # value = float(el.text.strip())
                value = float(el.text.strip().replace(',', ''))
                pixel = float(el.get("y", 0))
                y_axis_data.append((pixel, value))
            except (ValueError, TypeError):
                continue

        if len(y_axis_data) < 2:
            raise ValueError("Not enough Y-axis labels to infer scale.")

        # Sort top to bottom by pixel
        y_axis_data.sort(key=lambda x: x[0])
        y_min_pixel, y_min_value = y_axis_data[0]
        y_max_pixel, y_max_value = y_axis_data[-1]

        # 2. Parse SVG path Y values
        path = container.select_one(svg_path_selector)
        if not path:
            raise ValueError(f"SVG path not found: {svg_path_selector}")

        d_attr = path.get("d", "")
        raw_y_coords = re.findall(r"[ML]\s*\d+\.?\d*\s+(\d+\.?\d*)", d_attr)
        if not raw_y_coords:
            raise ValueError("No Y values found in SVG path.")

        # Detect and apply Y offset from 'transform="translate(...,Y)"'
        y_offset = 0
        series_group = path.find_parent("g")
        if series_group and series_group.has_attr("transform"):
            match = re.search(r"translate\(\s*\d+\.?\d*,\s*(\d+\.?\d*)\)", series_group["transform"])
            if match:
                y_offset = float(match.group(1))

        y_coords = [float(y) + y_offset for y in raw_y_coords]

        # 3. Map Y-coordinates to actual values
        def map_y(y_pixel: float) -> float:
            proportion = (y_pixel - y_min_pixel) / (y_max_pixel - y_min_pixel)
            return round(y_min_value + proportion * (y_max_value - y_min_value), 2)

        y_values = [map_y(y) for y in y_coords]

        # 4. Get X-axis labels (e.g. months)
        x_labels = [el.text.strip() for el in container.select(x_label_selector)]

        if len(x_labels) != len(y_values):
            raise ValueError(f"Mismatch: {len(x_labels)} x-labels vs {len(y_values)} y-values")

        return [
            {x_key: x, y_key: y}
            for x, y in zip(x_labels, y_values)
        ]


if __name__ == "__main__":
    # For manual testing of PageParser methods
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
    sample_path = os.path.join(raw_html_dir, html_filenames[0])

    with open(sample_path, "r", encoding="utf-8") as f:
        html = f.read()

    print(f"Parsing file: {html_filenames[0]}")
    # pprint(html)

    parser = PageParser(html)

    print("global_rank: ")
    extract_global_rank = parser.extract_from_nested(
        parent_selector="div.wa-rank-list__item.wa-rank-list__item--global",
        child_selector="p.wa-rank-list__value")
    print(extract_global_rank)

    print("total_visits: ")
    extract_total_visits = parser.extract_from_nested(
        parent_selector="div.wa-overview__column.wa-overview__column--engagement",
        child_selector="p.engagement-list__item-value")
    print(extract_total_visits)

    print("bounce_rate: ")
    extract_bounce_rate = parser.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="bounce-rate",
        value_selector="p.engagement-list__item-value")
    print(extract_bounce_rate)

    print("pages_per_visit: ")
    extract_pages_per_visit = parser.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="pages-per-visit",
        value_selector="p.engagement-list__item-value")
    print(extract_pages_per_visit)

    print("avg_visit_duration: ")
    extract_avg_visit_duration = parser.extract_from_nested_by_attribute(
        container_selector="div.engagement-list__item",
        label_tag="p",
        label_attr="data-test",
        label_value="avg-visit-duration",
        value_selector="p.engagement-list__item-value")
    print(extract_avg_visit_duration)

    print("rank_changes: ")
    extract_rank_changes = parser.extract_line_chart_from_svg_path_auto(
        container_selector="div.wa-ranking__main-content",
        x_label_selector="g.highcharts-axis-labels.highcharts-xaxis-labels text",
        svg_path_selector="g.highcharts-series path.highcharts-graph",
        y_axis_label_selector="g.highcharts-axis-labels.highcharts-yaxis-labels text",
        x_key="month",
        y_key="rank")
    pprint(extract_rank_changes)

    print("monthly_visits: ")
    extract_monthly_visits = parser.extract_paired_lists_from_selectors(
        container_selector="div.wa-traffic__chart",
        label_selector="g.highcharts-axis-labels.highcharts-xaxis-labels text",
        value_selector="tspan.wa-traffic__chart-data-label",
        label_key="month",
        value_key="visits")
    pprint(extract_monthly_visits)

    print("last_month_change: ")
    extract_traffic_change = parser.extract_from_nested_by_label_text(
        container_selector="div.wa-traffic__engagement-item",
        label_tag="span.wa-traffic__engagement-item-title",
        label_text="Last Month Change",
        value_selector="span.wa-traffic__engagement-item-value")
    print(extract_traffic_change)

    print("top_countries: ")
    extract_top_countries = parser.extract_repeating_labeled_items(
        item_selector="div.wa-geography__country.wa-geography__legend-item",
        label_selector="a.wa-geography__country-name, span.wa-geography__country-name",
        value_selector="span.wa-geography__country-traffic-value")
    pprint(extract_top_countries)

    print("age_distribution: ")
    extract_age_distribution = parser.extract_paired_lists_from_selectors(
        container_selector="div.wa-demographics__age",
        label_selector="g.highcharts-axis-labels.highcharts-xaxis-labels text",
        value_selector="tspan.wa-demographics__age-data-label",
        label_key="age_group",
        value_key="percentage")
    pprint(extract_age_distribution)









