import pytest
import sys
import os
import io
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli import CLI
from src.database import DatabaseManager


class TestCLI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.db_path = "test_cli.db"
        self.cli = CLI()
        self.cli.db = DatabaseManager(self.db_path)
        self.cli.db.init_db()
        yield
        self.cli.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_user(self):
        self.cli.add_user(["John", "IT", "3", "Room 101"])
        users = self.cli.db.get_all_users()
        assert len(users) == 1
        assert users[0].name == "John"

    def test_list_users(self):
        self.cli.add_user(["John", "IT", "3"])
        self.cli.add_user(["Jane", "HR", "2"])
        self.cli.list_users([])

    def test_add_access_log(self):
        user_id = self.cli.db.create_user(
            type('User', (), {'name': 'John', 'department': 'IT', 'access_level': 3, 'assigned_room': None})()
        )
        self.cli.add_access_log([str(user_id), "Room 101", "granted"])
        logs = self.cli.db.get_all_access_logs()
        assert len(logs) == 1

    def test_request_access(self):
        user_id = self.cli.db.create_user(
            type('User', (), {'name': 'John', 'department': 'IT', 'access_level': 3, 'assigned_room': 'Room 101'})()
        )
        self.cli.request_access([str(user_id), "Room 101"])

    def test_list_alerts(self):
        user_id = self.cli.db.create_user(
            type('User', (), {'name': 'John', 'department': 'IT', 'access_level': 3, 'assigned_room': None})()
        )
        self.cli.add_access_log([str(user_id), "Room 999", "denied"])
        self.cli.list_alerts([])

    def test_parse_command(self):
        cmd, args = self.cli.parse_command("add_user John IT 3")
        assert cmd == "add_user"
        assert args == ["John", "IT", "3"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])