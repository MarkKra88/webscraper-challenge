import functools
import datetime
import traceback
import csv
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "logs", "error_log.csv")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def error_logger(func):
    """
    Decorator for logging exceptions to a CSV file and returning a fallback value.
    Helps identify where parsing failed without breaking the pipeline.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Collect error metadata
            class_name = args[0].__class__.__name__ if args else "UnknownClass"
            method_name = func.__name__
            timestamp = datetime.datetime.now().isoformat()
            error_msg = str(e)
            trace = traceback.format_exc()

            # Notify in console (non-blocking)
            print(f"An error occurred in {class_name}.{method_name}() — details logged.")

            # Save error details to CSV log
            with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, class_name, method_name, error_msg, trace])

            return "__MISSING__"
    return wrapper
