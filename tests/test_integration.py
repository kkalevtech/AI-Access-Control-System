import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager
from src.events import EventDispatcher, AccessEventArgs, AlertEventArgs, SuspiciousBehaviorEventArgs
from src.controllers import AccessController, SecurityManager
from src.files import FileManager
from src.models import User, AccessLog, Alert


class TestIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.db_path = "test_integration.db"
        self.db = DatabaseManager(self.db_path)
        self.db.init_db()
        self.dispatcher = EventDispatcher()
        self.fm = FileManager()
        self.access_controller = AccessController(self.db, self.dispatcher)
        self.security_manager = SecurityManager(self.db, self.dispatcher, self.fm)

        self.dispatcher.register_listener('on_suspicious_behavior', self.security_manager.on_suspicious_behavior_handler)
        self.dispatcher.register_listener('on_access_denied', self.security_manager.on_access_denied_handler)
        self.dispatcher.register_listener('on_multiple_attempts', self.security_manager.on_multiple_attempts_handler)

        yield
        self.db.close()
        for f in [self.db_path, "system.log"]:
            if os.path.exists(f):
                os.remove(f)

    def test_full_user_flow(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)

        retrieved_user = self.db.get_user(user_id)
        assert retrieved_user is not None
        assert retrieved_user.name == "John Smith"

    def test_full_access_request_flow(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)

        result = self.access_controller.request_access(user_id, "Room 101")

        assert result['granted'] is True

    def test_full_denied_access_flow(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)

        result = self.access_controller.request_access(user_id, "Room 999")

        assert result['granted'] is False

    def test_event_dispatch_to_listeners(self):
        alert_received = []

        def listener1(args):
            alert_received.append(('listener1', args.user_id))

        def listener2(args):
            alert_received.append(('listener2', args.user_id))

        self.dispatcher.register_listener('on_suspicious_behavior', listener1)
        self.dispatcher.register_listener('on_suspicious_behavior', listener2)

        event_args = SuspiciousBehaviorEventArgs(
            user_id=1,
            score=0.8,
            reason="Test",
            timestamp="2024-01-15 09:30:00"
        )
        self.dispatcher.dispatch_event('on_suspicious_behavior', event_args)

        assert len(alert_received) == 2
        assert alert_received[0][0] == 'listener1'
        assert alert_received[1][0] == 'listener2'

    def test_security_manager_triggers_alert(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)

        event_args = AlertEventArgs(
            user_id=user_id,
            alert_type='test_alert',
            description='Test alert',
            created_at='2024-01-15 09:30:00'
        )
        self.security_manager.handle_alert(event_args)

        alerts = self.db.get_user_alerts(user_id)
        assert len(alerts) == 1
        assert alerts[0].alert_type == 'test_alert'

    def test_multiple_attempts_detection(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)

        now = datetime.now()
        for i in range(5):
            past_time = (now - timedelta(minutes=i*5)).strftime("%Y-%m-%d %H:%M:%S")
            log = AccessLog(
                user_id=user_id,
                access_time=past_time,
                location='Room 999',
                status='denied',
                attempts_count=1
            )
            self.db.create_access_log(log)

        result = self.security_manager.monitor_failed_attempts(user_id, 60)

        assert result['is_suspicious'] is True

    def test_file_logging(self):
        self.fm.write_log("Test log message")

        lines = self.fm.read_log("system.log")
        assert len(lines) == 1
        assert "Test log message" in lines[0]

    def test_database_persistence(self):
        user = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user_id = self.db.create_user(user)

        self.db.close()
        self.db = DatabaseManager(self.db_path)
        self.db.init_db()

        retrieved = self.db.get_user(user_id)
        assert retrieved is not None
        assert retrieved.name == "John Smith"

    def test_full_system_integration(self):
        user1 = User(name="John Smith", department="IT", access_level=3, assigned_room="Room 101")
        user1_id = self.db.create_user(user1)

        user2 = User(name="Jane Doe", department="HR", access_level=2, assigned_room="Room 205")
        user2_id = self.db.create_user(user2)

        result = self.access_controller.request_access(user1_id, "Room 101")
        assert result['granted'] is True

        result = self.access_controller.request_access(user2_id, "Room 999")
        assert result['granted'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])