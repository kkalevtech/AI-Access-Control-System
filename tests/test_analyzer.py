import pytest
import os
import tempfile
from datetime import datetime, timedelta

from src.ai.analyzer import BehaviorAnalyzer
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
def analyzer(temp_db):
    return BehaviorAnalyzer(temp_db)


@pytest.fixture
def sample_users(temp_db):
    users = [
        User(name="Alice", department="IT", access_level=3, assigned_room="IT-101"),
        User(name="Bob", department="HR", access_level=2, assigned_room="HR-201"),
        User(name="Charlie", department="Finance", access_level=4, assigned_room="FIN-301"),
    ]
    for user in users:
        temp_db.create_user(user)
    return users


class TestIsNightAccess:
    def test_night_hours(self, analyzer):
        assert analyzer.is_night_access(22) is True
        assert analyzer.is_night_access(23) is True
        assert analyzer.is_night_access(0) is True
        assert analyzer.is_night_access(1) is True
        assert analyzer.is_night_access(5) is True

    def test_day_hours(self, analyzer):
        assert analyzer.is_night_access(6) is False
        assert analyzer.is_night_access(12) is False
        assert analyzer.is_night_access(18) is False
        assert analyzer.is_night_access(21) is False


class TestIsAssignedRoom:
    def test_matching_room(self, analyzer, sample_users):
        assert analyzer.is_assigned_room(1, "IT-101") is True

    def test_non_matching_room(self, analyzer, sample_users):
        assert analyzer.is_assigned_room(1, "HR-201") is False

    def test_nonexistent_user(self, analyzer):
        assert analyzer.is_assigned_room(999, "IT-101") is False


class TestGetAccessFrequency:
    def test_no_logs(self, analyzer, sample_users):
        assert analyzer.get_access_frequency(1, 60) == 0

    def test_with_logs(self, analyzer, temp_db, sample_users):
        now = datetime.now()
        for i in range(5):
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(minutes=i*10)).isoformat(),
                location="IT-101",
                status="granted"
            )
            temp_db.create_access_log(log)
        assert analyzer.get_access_frequency(1, 60) == 5


class TestGetHistoricalDeniedCount:
    def test_no_denied(self, analyzer, sample_users):
        assert analyzer.get_historical_denied_count(1) == 0

    def test_with_denied(self, analyzer, temp_db, sample_users):
        now = datetime.now()
        for status in ['granted', 'denied', 'denied', 'granted']:
            log = AccessLog(
                user_id=1,
                access_time=now.isoformat(),
                location="IT-101",
                status=status
            )
            temp_db.create_access_log(log)
        assert analyzer.get_historical_denied_count(1) == 2


class TestExtractFeatures:
    def test_basic_extraction(self, analyzer, sample_users):
        features = analyzer.extract_features(1, datetime.now().isoformat(), "IT-101")
        assert 'hour' in features
        assert 'minute' in features
        assert 'day_of_week' in features
        assert 'is_weekend' in features
        assert 'access_count_last_hour' in features
        assert 'is_assigned_room' in features
        assert 'user_access_level' in features

    def test_non_assigned_room(self, analyzer, sample_users):
        features = analyzer.extract_features(1, datetime.now().isoformat(), "HR-201")
        assert features['is_assigned_room'] == 0

    def test_nonexistent_user(self, analyzer, sample_users):
        features = analyzer.extract_features(999, datetime.now().isoformat(), "IT-101")
        assert features['is_assigned_room'] == 0
        assert features['user_access_level'] == 1

    def test_different_department(self, analyzer, sample_users):
        features = analyzer.extract_features(1, datetime.now().isoformat(), "FIN-301")
        assert features['is_same_department'] == 0

    def test_weekend_access(self, analyzer, sample_users):
        saturday = datetime(2024, 1, 6, 10, 0, 0)
        features = analyzer.extract_features(1, saturday.isoformat(), "IT-101")
        assert features['is_weekend'] == 1


class TestTrainFromDatabase:
    def test_insufficient_data(self, analyzer, sample_users):
        result = analyzer.train_from_database()
        assert 'error' in result

    def test_sufficient_data(self, analyzer, temp_db, sample_users):
        now = datetime.now()
        for i in range(35):
            hour = 10 if i % 2 == 0 else 23
            location = "IT-101" if i % 3 == 0 else "HR-201"
            status = "granted" if i % 4 == 0 else "denied"
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location=location,
                status=status
            )
            temp_db.create_access_log(log)
        result = analyzer.train_from_database()
        assert 'num_samples' in result
        assert analyzer.is_trained is True


class TestSaveLoadModel:
    def test_save_and_load(self, analyzer, temp_db, sample_users):
        now = datetime.now()
        for i in range(35):
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location="IT-101",
                status="granted"
            )
            temp_db.create_access_log(log)

        analyzer.train_from_database()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            filepath = f.name

        try:
            assert analyzer.save_model(filepath) is True
            new_analyzer = BehaviorAnalyzer(temp_db)
            assert new_analyzer.load_model(filepath) is True
            assert new_analyzer.is_trained is True
        finally:
            os.unlink(filepath)

    def test_load_nonexistent_file(self, analyzer):
        result = analyzer.load_model('nonexistent.pkl')
        assert result is False

    def test_save_to_invalid_path(self, analyzer, temp_db, sample_users):
        now = datetime.now()
        for i in range(35):
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location="IT-101",
                status="granted"
            )
            temp_db.create_access_log(log)

        analyzer.train_from_database()
        result = analyzer.save_model('/invalid/path/model.pkl')
        assert result is False


class TestAnalyze:
    def test_untrained_model(self, analyzer, sample_users):
        result = analyzer.analyze(1, datetime.now().isoformat(), "IT-101")
        assert 'error' in result

    def test_trained_model(self, analyzer, temp_db, sample_users):
        now = datetime.now()
        for i in range(35):
            hour = 10 if i % 2 == 0 else 23
            location = "IT-101" if i % 3 == 0 else "HR-201"
            status = "granted" if i % 4 == 0 else "denied"
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location=location,
                status=status
            )
            temp_db.create_access_log(log)

        analyzer.train_from_database()
        result = analyzer.analyze(1, datetime.now().isoformat(), "IT-101")

        assert 'classification' in result
        assert 'confidence_normal' in result
        assert 'confidence_suspicious' in result
        assert result['classification'] in ["Normal", "Suspicious"]


class TestRetrain:
    def test_retrain(self, analyzer, temp_db, sample_users):
        now = datetime.now()
        for i in range(35):
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location="IT-101",
                status="granted"
            )
            temp_db.create_access_log(log)

        analyzer.train_from_database()
        assert analyzer.is_trained is True

        result = analyzer.retrain()
        assert 'num_samples' in result


class TestPredictionConfidence:
    def test_confidence_scores(self, analyzer, temp_db, sample_users):
        now = datetime.now()
        for i in range(35):
            hour = 10 if i % 2 == 0 else 23
            location = "IT-101" if i % 3 == 0 else "HR-201"
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location=location,
                status="granted"
            )
            temp_db.create_access_log(log)

        analyzer.train_from_database()
        features = analyzer.extract_features(1, datetime.now().isoformat(), "IT-101")
        confidence = analyzer.get_prediction_confidence(features)

        assert 'normal_prob' in confidence
        assert 'suspicious_prob' in confidence
        assert 0 <= confidence['normal_prob'] <= 1
        assert 0 <= confidence['suspicious_prob'] <= 1