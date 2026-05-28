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

    def export_users_to_json(self, filepath, users):
        data = [user.to_dict() for user in users]
        self.write_json(filepath, data)

    def export_access_logs_to_csv(self, filepath, logs):
        if not logs:
            return
        fieldnames = ['id', 'user_id', 'access_time', 'is_weekend', 'location', 'status', 'room_id']
        data = [log.to_dict() for log in logs]
        self.write_csv(filepath, data, fieldnames)

    def import_users_from_json(self, filepath):
        data = self.read_json(filepath)
        from src.models import User
        return [User.from_dict(user_data) for user_data in data]

    def import_access_logs_from_csv(self, filepath):
        data = self.read_csv(filepath)
        from src.models import AccessLog
        return [AccessLog.from_dict(log_data) for log_data in data]

    def backup_database(self, db_manager, backup_path):
        try:
            import shutil
            shutil.copy2(db_manager.db_path, backup_path)
            return True
        except Exception:
            return False

    def restore_database(self, db_manager, backup_path):
        try:
            import shutil
            db_manager.close()
            shutil.copy2(backup_path, db_manager.db_path)
            db_manager.connect()
            return True
        except Exception:
            return False