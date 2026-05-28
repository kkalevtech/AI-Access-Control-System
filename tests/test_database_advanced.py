import pytest
import os
import tempfile
from datetime import datetime, timedelta

from src.database.database_manager import DatabaseManager
from src.models import User, AccessLog


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = DatabaseManager(path)
    db.init_db()
    yield db
    db.close()
    os.unlink(path)


@pytest.fixture
def sample_data(temp_db):
    users = []
    for i, name in enumerate(['Alice', 'Bob', 'Charlie'], start=1):
        user = User(name=name, department='IT', access_level=3, assigned_room='IT-101')
        user.id = temp_db.create_user(user)
        users.append(user)

    now = datetime.now()
    for i, user in enumerate(users):
        for j in range(5):
            log = AccessLog(
                user_id=user.id,
                access_time=(now - timedelta(days=j)).isoformat(),
                location='IT-101',
                status='granted' if j % 3 != 0 else 'denied'
            )
            temp_db.create_access_log(log)
    return temp_db


class TestGetUserAccessCount:
    def test_get_user_access_count(self, sample_data):
        count = sample_data.get_user_access_count(1)
        assert count == 5

    def test_get_user_access_count_no_data(self, temp_db):
        count = temp_db.get_user_access_count(999)
        assert count == 0


class TestGetUserAccessCountByStatus:
    def test_get_granted_count(self, sample_data):
        count = sample_data.get_user_access_count_by_status(1, 'granted')
        assert count >= 3

    def test_get_denied_count(self, sample_data):
        count = sample_data.get_user_access_count_by_status(1, 'denied')
        assert count >= 1


class TestGetLocationAccessCount:
    def test_get_location_count(self, sample_data):
        count = sample_data.get_location_access_count('IT-101')
        assert count >= 5

    def test_get_location_count_nonexistent(self, sample_data):
        count = sample_data.get_location_access_count('XYZ-999')
        assert count == 0


class TestGetDepartmentAccessStats:
    def test_get_department_stats(self, sample_data):
        stats = sample_data.get_department_access_stats('IT')
        assert stats['total'] >= 5
        assert stats['granted'] >= 3
        assert stats['denied'] >= 1

    def test_get_department_stats_nonexistent(self, sample_data):
        stats = sample_data.get_department_access_stats('Unknown')
        assert stats['total'] == 0


class TestGetAccessLogsByDateRange:
    def test_get_logs_by_date_range(self, sample_data):
        now = datetime.now()
        start = (now - timedelta(days=10)).isoformat()
        end = now.isoformat()
        logs = sample_data.get_access_logs_by_date_range(start, end)
        assert len(logs) >= 5

    def test_get_logs_no_results(self, sample_data):
        start = (datetime.now() - timedelta(days=30)).isoformat()
        end = (datetime.now() - timedelta(days=20)).isoformat()
        logs = sample_data.get_access_logs_by_date_range(start, end)
        assert len(logs) == 0


class TestGetMostActiveUsers:
    def test_get_most_active_users(self, sample_data):
        result = sample_data.get_most_active_users(limit=5)
        assert len(result) >= 1
        assert 'user_id' in result[0]
        assert 'access_count' in result[0]


class TestGetSuspiciousUsers:
    def test_get_suspicious_users(self, sample_data):
        result = sample_data.get_suspicious_users(days=7)
        assert isinstance(result, list)

    def test_get_suspicious_users_single_user(self, temp_db):
        user = User(name='Test', department='IT', access_level=1, assigned_room='IT-101')
        temp_db.create_user(user)

        now = datetime.now()
        for i in range(4):
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location='HR-201',
                status='denied'
            )
            temp_db.create_access_log(log)

        result = temp_db.get_suspicious_users(days=1)
        assert len(result) >= 1