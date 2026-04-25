import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager
from src.models import User, AccessLog, Alert


class TestDatabaseManager:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.db_path = "test_database.db"
        self.db = DatabaseManager(self.db_path)
        self.db.init_db()
        yield
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_init_db_creates_tables(self):
        result = self.db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert len(result) == 1
        result = self.db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='access_logs'")
        assert len(result) == 1
        result = self.db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'")
        assert len(result) == 1

    def test_create_user(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)
        assert user_id is not None
        assert user_id > 0

    def test_get_user(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)
        retrieved = self.db.get_user(user_id)
        assert retrieved is not None
        assert retrieved.name == "John Smith"
        assert retrieved.department == "IT"
        assert retrieved.access_level == 3

    def test_get_all_users(self):
        user1 = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user2 = User(name="Jane Doe", department="HR", access_level=2, assigned_room="Room 205")
        self.db.create_user(user1)
        self.db.create_user(user2)
        users = self.db.get_all_users()
        assert len(users) == 2

    def test_update_user(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)
        self.db.update_user(user_id, name="John Updated", access_level=5)
        updated = self.db.get_user(user_id)
        assert updated.name == "John Updated"
        assert updated.access_level == 5

    def test_delete_user(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)
        result = self.db.delete_user(user_id)
        assert result is True
        retrieved = self.db.get_user(user_id)
        assert retrieved is None

    def test_create_access_log(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)
        log = AccessLog(user_id=user_id, access_time="2024-01-15 09:30:00", location="Room 101", status="granted", attempts_count=1)
        log_id = self.db.create_access_log(log)
        assert log_id is not None
        assert log_id > 0

    def test_get_access_log(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)
        log = AccessLog(user_id=user_id, access_time="2024-01-15 09:30:00", location="Room 101", status="granted", attempts_count=1)
        log_id = self.db.create_access_log(log)
        retrieved = self.db.get_access_log(log_id)
        assert retrieved is not None
        assert retrieved.location == "Room 101"
        assert retrieved.status == "granted"

    def test_get_all_access_logs(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)
        log1 = AccessLog(user_id=user_id, access_time="2024-01-15 09:30:00", location="Room 101", status="granted", attempts_count=1)
        log2 = AccessLog(user_id=user_id, access_time="2024-01-15 10:30:00", location="Room 102", status="denied", attempts_count=1)
        self.db.create_access_log(log1)
        self.db.create_access_log(log2)
        logs = self.db.get_all_access_logs()
        assert len(logs) == 2

    def test_get_user_access_logs(self):
        user1 = User(name="John Smith", department="IT", access_level=3)
        user2 = User(name="Jane Doe", department="HR", access_level=2)
        user1_id = self.db.create_user(user1)
        user2_id = self.db.create_user(user2)
        log1 = AccessLog(user_id=user1_id, access_time="2024-01-15 09:30:00", location="Room 101", status="granted", attempts_count=1)
        log2 = AccessLog(user_id=user2_id, access_time="2024-01-15 09:30:00", location="Room 101", status="granted", attempts_count=1)
        self.db.create_access_log(log1)
        self.db.create_access_log(log2)
        user1_logs = self.db.get_user_access_logs(user1_id)
        assert len(user1_logs) == 1

    def test_delete_access_log(self):
        user = User(name="John Smith", department="IT", access_level=3)
        user_id = self.db.create_user(user)
        log = AccessLog(user_id=user_id, access_time="2024-01-15 09:30:00", location="Room 101", status="granted", attempts_count=1)
        log_id = self.db.create_access_log(log)
        result = self.db.delete_access_log(log_id)
        assert result is True

    def test_create_alert(self):
        user = User(name="John Smith", department="IT", access_level=3)
        user_id = self.db.create_user(user)
        alert = Alert(user_id=user_id, alert_type="access_denied", description="Unauthorized access", created_at="2024-01-15 09:30:00")
        alert_id = self.db.create_alert(alert)
        assert alert_id is not None
        assert alert_id > 0

    def test_get_alert(self):
        user = User(name="John Smith", department="IT", access_level=3)
        user_id = self.db.create_user(user)
        alert = Alert(user_id=user_id, alert_type="access_denied", description="Unauthorized access", created_at="2024-01-15 09:30:00")
        alert_id = self.db.create_alert(alert)
        retrieved = self.db.get_alert(alert_id)
        assert retrieved is not None
        assert retrieved.alert_type == "access_denied"

    def test_get_all_alerts(self):
        user = User(name="John Smith", department="IT", access_level=3)
        user_id = self.db.create_user(user)
        alert1 = Alert(user_id=user_id, alert_type="access_denied", description="Test 1", created_at="2024-01-15 09:30:00")
        alert2 = Alert(user_id=user_id, alert_type="suspicious_behavior", description="Test 2", created_at="2024-01-15 10:30:00")
        self.db.create_alert(alert1)
        self.db.create_alert(alert2)
        alerts = self.db.get_all_alerts()
        assert len(alerts) == 2

    def test_get_user_alerts(self):
        user1 = User(name="John Smith", department="IT", access_level=3)
        user2 = User(name="Jane Doe", department="HR", access_level=2)
        user1_id = self.db.create_user(user1)
        user2_id = self.db.create_user(user2)
        alert1 = Alert(user_id=user1_id, alert_type="access_denied", description="Test", created_at="2024-01-15 09:30:00")
        alert2 = Alert(user_id=user2_id, alert_type="access_denied", description="Test", created_at="2024-01-15 09:30:00")
        self.db.create_alert(alert1)
        self.db.create_alert(alert2)
        user1_alerts = self.db.get_user_alerts(user1_id)
        assert len(user1_alerts) == 1

    def test_delete_alert(self):
        user = User(name="John Smith", department="IT", access_level=3)
        user_id = self.db.create_user(user)
        alert = Alert(user_id=user_id, alert_type="access_denied", description="Test", created_at="2024-01-15 09:30:00")
        alert_id = self.db.create_alert(alert)
        result = self.db.delete_alert(alert_id)
        assert result is True

    def test_execute_query(self):
        user = User(name="John Smith", department="IT", access_level=3)
        user_id = self.db.create_user(user)
        result = self.db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
        assert len(result) == 1
        assert result[0]['name'] == "John Smith"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])