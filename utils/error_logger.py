import functools
import datetime
import traceback
import csv
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "logs", "error_log.csv")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def error_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        filename = kwargs.get("filename", "unknown.html")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            class_name = args[0].__class__.__name__ if args else "UnknownClass"
            method_name = func.__name__
            timestamp = datetime.datetime.now().isoformat()
            error_msg = str(e)
            trace = traceback.format_exc()

            # Console log
            print("\n--- ERROR LOG ---")
            print(f"[{timestamp}] File: {filename}")
            print(f"Exception in {class_name}.{method_name}()")
            print(f"Error: {error_msg}")
            print("--- END LOG ---\n")

            # Save to CSV
            with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["-" * 80])
                writer.writerow([timestamp, filename, class_name, method_name, error_msg, trace])
        return None
    return wrapper