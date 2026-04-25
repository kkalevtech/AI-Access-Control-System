import csv
import json
from datetime import datetime


class FileManager:
    def write_log(self, message, log_file="system.log"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def read_log(self, log_file="system.log"):
        try:
            with open(log_file, "r") as f:
                return f.readlines()
        except FileNotFoundError:
            return []

    def read_json(self, file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON in file: {file_path}")

    def write_json(self, file_path, data):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def read_csv(self, file_path):
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except csv.Error as e:
            raise ValueError(f"Invalid CSV in file: {file_path}")

    def write_csv(self, file_path, data, fieldnames):
        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)