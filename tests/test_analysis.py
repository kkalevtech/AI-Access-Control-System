import pytest
import os
import tempfile
from datetime import datetime, timedelta

from src.analysis import (
    analyze_access_patterns,
    get_peak_access_hours,
    detect_anomalies,
    generate_access_report
)
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
def sample_logs(temp_db):
    now = datetime.now()
    user = User(name="Test", department="IT", access_level=1, assigned_room="IT-101")
    user.id = temp_db.create_user(user)

    logs = []
    for i in range(20):
        log = AccessLog(
            user_id=user.id,
            access_time=(now - timedelta(hours=i)).isoformat(),
            location="IT-101" if i % 2 == 0 else "HR-201",
            status="granted" if i % 3 != 0 else "denied"
        )
        log.id = temp_db.create_access_log(log)
        logs.append(log)
    return logs


class TestAnalyzeAccessPatterns:
    def test_analyze_with_data(self, sample_logs):
        result = analyze_access_patterns(sample_logs)
        assert result['total'] == 20
        assert result['granted'] >= 10
        assert result['success_rate'] > 0
        assert 'by_location' in result

    def test_analyze_empty(self):
        result = analyze_access_patterns([])
        assert result['total'] == 0
        assert result['success_rate'] == 0


class TestGetPeakAccessHours:
    def test_peak_hours(self, sample_logs):
        result = get_peak_access_hours(sample_logs)
        assert isinstance(result, list)
        if result:
            assert 'hour' in result[0]
            assert 'count' in result[0]

    def test_peak_hours_empty(self):
        result = get_peak_access_hours([])
        assert result == []


class TestDetectAnomalies:
    def test_detect_anomalies(self, sample_logs):
        result = detect_anomalies(sample_logs)
        assert 'high_frequency_users' in result
        assert 'unusual_locations' in result
        assert 'odd_time_patterns' in result

    def test_detect_anomalies_empty(self):
        result = detect_anomalies([])
        assert result['high_frequency_users'] == []
        assert result['unusual_locations'] == []


class TestGenerateAccessReport:
    def test_generate_report(self, temp_db):
        now = datetime.now()
        user = User(name="Test", department="IT", access_level=1, assigned_room="IT-101")
        user.id = temp_db.create_user(user)

        for i in range(10):
            log = AccessLog(
                user_id=user.id,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location="IT-101",
                status="granted"
            )
            temp_db.create_access_log(log)

        start = (now - timedelta(days=1)).isoformat()
        end = now.isoformat()

        result = generate_access_report(temp_db, start, end)
        assert 'total_access_attempts' in result
        assert 'success_rate' in result
        assert 'most_active_users' in result
        assert 'peak_hours' in result
        assert 'anomalies' in result

    def test_generate_report_no_data(self, temp_db):
        start = (datetime.now() - timedelta(days=30)).isoformat()
        end = (datetime.now() - timedelta(days=20)).isoformat()

        result = generate_access_report(temp_db, start, end)
        assert result['total_access_attempts'] == 0
        assert result['success_rate'] == 0


class TestLinQStyleOperations:
    def test_filter_operation(self):
        logs = [
            AccessLog(user_id=1, access_time=datetime.now().isoformat(), location="IT-101", status="granted"),
            AccessLog(user_id=2, access_time=datetime.now().isoformat(), location="HR-201", status="denied"),
        ]
        granted = list(filter(lambda log: log.status == 'granted', logs))
        assert len(granted) == 1

    def test_map_operation(self):
        logs = [
            AccessLog(user_id=1, access_time=datetime.now().isoformat(), location="IT-101", status="granted"),
            AccessLog(user_id=2, access_time=datetime.now().isoformat(), location="HR-201", status="denied"),
        ]
        locations = list(map(lambda log: log.location, logs))
        assert locations == ["IT-101", "HR-201"]

    def test_sorted_operation(self):
        logs = [
            AccessLog(id=2, user_id=1, access_time=datetime.now().isoformat(), location="B", status="granted"),
            AccessLog(id=1, user_id=1, access_time=datetime.now().isoformat(), location="A", status="granted"),
        ]
        sorted_logs = sorted(logs, key=lambda log: log.id)
        assert sorted_logs[0].id == 1