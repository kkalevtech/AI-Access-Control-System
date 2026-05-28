import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import User, AccessLog, Alert


class TestUser:
    def test_user_creation(self):
        user = User(id=1, name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        assert user.id == 1
        assert user.name == "John Smith"
        assert user.department == "IT"
        assert user.access_level == 3
        assert user.assigned_room == "Room 101"

    def test_user_to_dict(self):
        user = User(id=1, name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        d = user.to_dict()
        assert d['id'] == 1
        assert d['name'] == "John Smith"
        assert d['department'] == "IT"
        assert d['access_level'] == 3
        assert d['assigned_room'] == "Room 101"

    def test_user_from_dict(self):
        data = {'id': 1, 'name': "John Smith", 'department': "IT", 'access_level': 3, 'assigned_room': "Room 101"}
        user = User.from_dict(data)
        assert user.id == 1
        assert user.name == "John Smith"
        assert user.department == "IT"
        assert user.access_level == 3
        assert user.assigned_room == "Room 101"

    def test_user_repr(self):
        user = User(id=1, name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        r = repr(user)
        assert "User(id=1" in r
        assert "John Smith" in r


class TestAccessLog:
    def test_access_log_creation(self):
        log = AccessLog(id=1, user_id=1, access_time="2024-01-15 09:30:00", location="Room 101", status="granted", attempts_count=1)
        assert log.id == 1
        assert log.user_id == 1
        assert log.access_time == "2024-01-15 09:30:00"
        assert log.location == "Room 101"
        assert log.status == "granted"
        assert log.attempts_count == 1

    def test_access_log_to_dict(self):
        log = AccessLog(id=1, user_id=1, access_time="2024-01-15 09:30:00", location="Room 101", status="granted", attempts_count=1)
        d = log.to_dict()
        assert d['id'] == 1
        assert d['user_id'] == 1
        assert d['status'] == "granted"

    def test_access_log_from_dict(self):
        data = {'id': 1, 'user_id': 1, 'access_time': "2024-01-15 09:30:00", 'location': "Room 101", 'status': "denied", 'attempts_count': 2}
        log = AccessLog.from_dict(data)
        assert log.id == 1
        assert log.user_id == 1
        assert log.status == "denied"
        assert log.attempts_count == 2


class TestAlert:
    def test_alert_creation(self):
        alert = Alert(id=1, user_id=1, alert_type="access_denied", description="Unauthorized access attempt", created_at="2024-01-15 09:30:00")
        assert alert.id == 1
        assert alert.user_id == 1
        assert alert.alert_type == "access_denied"
        assert alert.description == "Unauthorized access attempt"
        assert alert.created_at == "2024-01-15 09:30:00"

    def test_alert_to_dict(self):
        alert = Alert(id=1, user_id=1, alert_type="suspicious_behavior", description="Multiple failed attempts", created_at="2024-01-15 09:30:00")
        d = alert.to_dict()
        assert d['id'] == 1
        assert d['user_id'] == 1
        assert d['alert_type'] == "suspicious_behavior"

    def test_alert_from_dict(self):
        data = {'id': 1, 'user_id': 1, 'alert_type': "suspicious_behavior", 'description': "Multiple failed attempts", 'created_at': "2024-01-15 09:30:00"}
        alert = Alert.from_dict(data)
        assert alert.id == 1
        assert alert.alert_type == "suspicious_behavior"
        assert alert.description == "Multiple failed attempts"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])