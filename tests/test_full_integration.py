import pytest
import os
import tempfile
from datetime import datetime, timedelta

from src.database.database_manager import DatabaseManager
from src.controllers.access_controller import AccessController
from src.controllers.security_manager import SecurityManager
from src.events.event_dispatcher import EventDispatcher
from src.events.event_args import AccessEventArgs, SuspiciousBehaviorEventArgs, AlertEventArgs
from src.ai.analyzer import BehaviorAnalyzer
from src.models import User, AccessLog, Alert
from src.files.file_manager import FileManager


@pytest.fixture
def test_database():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = DatabaseManager(path)
    db.init_db()
    yield db
    db.close()
    os.unlink(path)


class TestFullUserFlow:
    def test_full_user_flow(self, test_database):
        user = User(name="Test User", department="IT", access_level=3, assigned_room="IT-101")
        user_id = test_database.create_user(user)
        assert user_id > 0

        retrieved = test_database.get_user(user_id)
        assert retrieved.name == "Test User"
        assert retrieved.department == "IT"


class TestFullAccessRequestFlow:
    def test_full_access_request_with_ai(self, test_database):
        user = User(name="Alice", department="IT", access_level=3, assigned_room="IT-101")
        test_database.create_user(user)

        dispatcher = EventDispatcher()
        analyzer = BehaviorAnalyzer(test_database)

        now = datetime.now()
        for i in range(35):
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(hours=i)).isoformat(),
                location="IT-101",
                status="granted"
            )
            test_database.create_access_log(log)

        analyzer.train_from_database()
        assert analyzer.is_trained is True

        result = analyzer.analyze(1, now.isoformat(), "IT-101")
        assert 'classification' in result


class TestFullDeniedAccessFlow:
    def test_denied_access_triggers_event(self, test_database):
        user = User(name="Bob", department="IT", access_level=1, assigned_room="IT-101")
        test_database.create_user(user)

        dispatcher = EventDispatcher()
        security_manager = SecurityManager(test_database, dispatcher)
        dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)

        access_time = datetime.now().isoformat()
        event_args = AccessEventArgs(
            user_id=1,
            location="HR-201",
            reason="Unauthorized access attempt",
            timestamp=access_time
        )
        dispatcher.dispatch_event('on_access_denied', event_args)

        alerts = test_database.get_all_alerts()
        assert len(alerts) >= 1


class TestEventDispatchToListeners:
    def test_event_dispatch_flow(self, test_database):
        dispatcher = EventDispatcher()
        security_manager = SecurityManager(test_database, dispatcher)

        dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
        dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)
        dispatcher.register_listener("on_multiple_attempts", security_manager.on_multiple_attempts_handler)

        event_args = AlertEventArgs(
            user_id=1,
            alert_type='test',
            description='Test alert',
            created_at=datetime.now().isoformat()
        )
        dispatcher.dispatch_event('on_multiple_attempts', event_args)

        alerts = test_database.get_all_alerts()
        assert len(alerts) >= 1


class TestSecurityManagerTriggersAlert:
    def test_security_manager_creates_alerts(self, test_database):
        user = User(name="Test", department="IT", access_level=1, assigned_room="IT-101")
        test_database.create_user(user)

        dispatcher = EventDispatcher()
        security_manager = SecurityManager(test_database, dispatcher)

        event_args = SuspiciousBehaviorEventArgs(
            user_id=1,
            score=85.0,
            reason="Test suspicious behavior",
            timestamp=datetime.now().isoformat()
        )
        security_manager.on_suspicious_behavior_handler(event_args)

        alerts = test_database.get_user_alerts(1)
        assert len(alerts) >= 1


class TestMultipleAttemptsDetection:
    def test_multiple_attempts_detection(self, test_database):
        user = User(name="Test", department="IT", access_level=1, assigned_room="IT-101")
        test_database.create_user(user)

        now = datetime.now()
        for i in range(5):
            log = AccessLog(
                user_id=1,
                access_time=(now - timedelta(minutes=i*10)).isoformat(),
                location="HR-201",
                status="denied"
            )
            test_database.create_access_log(log)

        dispatcher = EventDispatcher()
        security_manager = SecurityManager(test_database, dispatcher)

        result = security_manager.monitor_failed_attempts(1, time_window_minutes=60)
        assert result['is_suspicious'] is True


class TestFileLogging:
    def test_file_logging_integration(self, test_database):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as f:
            log_path = f.name

        try:
            file_manager = FileManager()
            file_manager.write_log("Test log message", log_path)

            lines = file_manager.read_log(log_path)
            assert len(lines) >= 1
        finally:
            if os.path.exists(log_path):
                os.unlink(log_path)


class TestDatabasePersistence:
    def test_database_persistence(self, test_database):
        user = User(name="Persistence Test", department="IT", access_level=2, assigned_room="IT-102")
        user_id = test_database.create_user(user)

        test_database.close()

        test_database.connect()
        retrieved = test_database.get_user(user_id)
        assert retrieved.name == "Persistence Test"


class TestFullSystemIntegration:
    def test_complete_system_integration(self, test_database):
        user1 = User(name="Alice", department="IT", access_level=3, assigned_room="IT-101")
        user2 = User(name="Bob", department="HR", access_level=2, assigned_room="HR-201")

        test_database.create_user(user1)
        test_database.create_user(user2)

        dispatcher = EventDispatcher()
        analyzer = BehaviorAnalyzer(test_database)

        now = datetime.now()
        for user_id in [1, 2]:
            for i in range(20):
                log = AccessLog(
                    user_id=user_id,
                    access_time=(now - timedelta(hours=i)).isoformat(),
                    location="IT-101" if i % 2 == 0 else "HR-201",
                    status="granted" if i % 3 != 0 else "denied"
                )
                test_database.create_access_log(log)

        result = analyzer.train_from_database()
        assert analyzer.is_trained is True

        result = analyzer.analyze(1, now.isoformat(), "IT-101")
        assert 'classification' in result

        access_controller = AccessController(test_database, dispatcher)
        security_manager = SecurityManager(test_database, dispatcher)

        dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
        dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)
        dispatcher.register_listener("on_multiple_attempts", security_manager.on_multiple_attempts_handler)

        access_result = access_controller.request_access(1, "IT-101")
        assert 'granted' in access_result

        users = test_database.get_all_users()
        assert len(users) >= 2

        logs = test_database.get_all_access_logs()
        assert len(logs) >= 40