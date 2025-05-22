import re
from typing import Optional

class Normalizer:
    @staticmethod
    def normalize_number(value: str) -> Optional[int]:
        """
        Converts formatted large numbers like '9.1M', '87.0B' to int.
        """
        if not value:
            return None
        multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}
        match = re.match(r"([\d\.]+)\s*([KMB])", value.strip(), re.IGNORECASE)
        if match:
            number, suffix = match.groups()
            return int(float(number) * multipliers[suffix.upper()])
        try:
            # Remove commas for values like "1,234"
            return int(value.replace(',', '').strip())
        except ValueError:
            return None

    @staticmethod
    def normalize_percentage(value: str) -> Optional[float]:
        """
        Converts '55.43%' to 55.43 (or 0.5543 if preferred)
        """
        if not value:
            return None
        try:
            return float(value.strip().replace('%', ''))
        except ValueError:
            return None

    @staticmethod
    def normalize_duration(value: str) -> Optional[int]:
        """
        Converts '00:02:26' to total seconds (146)
        """
        if not value:
            return None
        parts = value.strip().split(":")
        try:
            parts = [int(p) for p in parts]
            while len(parts) < 3:
                parts.insert(0, 0)  # pad to [hh, mm, ss]
            hours, minutes, seconds = parts
            return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            return None

    @staticmethod
    def handle_missing(value: str) -> Optional[str]:
        """Converts known placeholders for missing data into None."""
        if not value:
            return None

        value_clean = value.strip().lower()
        if value_clean in ["--", "n/a", "na", "-"]:
            return None

        return value

    @staticmethod
    def normalize_rank(value: str) -> Optional[int]:
        """
        Converts '#7,435' to 7435
        """
        if not value:
            return None
        try:
            return int(value.strip().replace("#", "").replace(",", ""))
        except ValueError:
            return None

    @staticmethod
    def normalize_list_field(data: list[dict], key: str, steps: list) -> list[dict]:
        """
        Applies a list of normalization functions to a specific key in a list of dictionaries.

        Example:
            normalize_list_field(data, key="value", steps=[Normalizer.handle_missing, Normalizer.normalize_percentage])
        """
        if not isinstance(data, list):
            return data

        normalized = []
        for item in data:
            if key in item:
                value = item[key]
                for step in steps:
                    value = step(value)
                item[key] = value
            normalized.append(item)

        return normalized

if __name__ == "__main__":
    print("normalize_number: ", Normalizer.normalize_number("10.5M"))
    print("normalize_percentage: ", Normalizer.normalize_percentage("55.43%"))
    print("normalize_duration: ", Normalizer.normalize_duration("00:03:16"))
    print("handle_missing: ", Normalizer.handle_missing("--"))
    print("normalize_rank: ", Normalizer.normalize_rank("#7,435"))
