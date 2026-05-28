import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager
from src.events import EventDispatcher, AccessEventArgs, AlertEventArgs, SuspiciousBehaviorEventArgs
from src.controllers import AccessController, SecurityManager
from src.files import FileManager
from src.models import User, AccessLog


class TestAccessController:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.db_path = "test_controllers.db"
        self.db = DatabaseManager(self.db_path)
        self.db.init_db()
        self.dispatcher = EventDispatcher()
        self.controller = AccessController(self.db, self.dispatcher)

        self.user_id = self.db.create_user(
            type('User', (), {'name': 'John', 'department': 'IT', 'access_level': 3, 'assigned_room': 'Room 101'})()
        )

        yield
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_grant_access(self):
        result = self.controller.grant_access(self.user_id, "Room 101", "2024-01-15 09:30:00")
        assert result['granted'] is True
        assert result['reason'] == 'Access granted'

    def test_deny_access(self):
        result = self.controller.deny_access(self.user_id, "Room 999", "Not authorized", "2024-01-15 09:30:00")
        assert result['granted'] is False
        logs = self.db.get_user_access_logs(self.user_id)
        assert len(logs) == 1
        assert logs[0].status == 'denied'

    def test_request_access_granted(self):
        result = self.controller.request_access(self.user_id, "Room 101")
        assert result['granted'] is True

    def test_request_access_denied(self):
        result = self.controller.request_access(self.user_id, "Room 999")
        assert result['granted'] is False

    def test_request_access_user_not_found(self):
        result = self.controller.request_access(999, "Room 101")
        assert result['granted'] is False
        assert 'User not found' in result.get('reason', '')

    def test_request_access_with_ai(self):
        from src.ai.analyzer import BehaviorAnalyzer
        now = datetime.now()
        for i in range(35):
            self.db.create_access_log(
                type('Log', (), {
                    'user_id': self.user_id,
                    'access_time': (now - timedelta(hours=i)).isoformat(),
                    'location': 'Room 101',
                    'status': 'granted',
                    'attempts_count': 1
                })()
            )

        self.controller.analyzer.train_from_database()
        result = self.controller.request_access(self.user_id, "Room 101", now.isoformat())
        assert 'classification' in result
        assert 'granted' in result

    def test_request_access_grant_with_analysis(self):
        from src.ai.analyzer import BehaviorAnalyzer
        now = datetime.now()
        for i in range(35):
            self.db.create_access_log(
                type('Log', (), {
                    'user_id': self.user_id,
                    'access_time': (now - timedelta(hours=i)).isoformat(),
                    'location': 'Room 101',
                    'status': 'granted',
                    'attempts_count': 1
                })()
            )

        self.controller.analyzer.train_from_database()
        result = self.controller.request_access(self.user_id, "Room 101", now.isoformat())
        assert result.get('classification') in ['Normal', 'Suspicious']


class TestSecurityManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.db_path = "test_security.db"
        self.db = DatabaseManager(self.db_path)
        self.db.init_db()
        self.dispatcher = EventDispatcher()
        self.fm = FileManager()
        self.security = SecurityManager(self.db, self.dispatcher, self.fm)

        self.user_id = self.db.create_user(
            type('User', (), {'name': 'John', 'department': 'IT', 'access_level': 3, 'assigned_room': 'Room 101'})()
        )

        yield
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists("system.log"):
            os.remove("system.log")

    def test_handle_alert(self):
        event_args = AlertEventArgs(
            user_id=self.user_id,
            alert_type='test_alert',
            description='Test alert',
            created_at='2024-01-15 09:30:00'
        )
        self.security.handle_alert(event_args)
        alerts = self.db.get_all_alerts()
        assert len(alerts) == 1
        assert alerts[0].alert_type == 'test_alert'

    def test_log_denied_access(self):
        self.security.log_denied_access(self.user_id, "Room 999", "Not authorized", "2024-01-15 09:30:00")
        alerts = self.db.get_user_alerts(self.user_id)
        assert len(alerts) == 1
        assert alerts[0].alert_type == 'access_denied'

    def test_monitor_failed_attempts(self):
        now = datetime.now()
        for i in range(5):
            past_time = (now - timedelta(minutes=i*5)).strftime("%Y-%m-%d %H:%M:%S")
            self.db.create_access_log(
                type('Log', (), {
                    'user_id': self.user_id,
                    'access_time': past_time,
                    'location': 'Room 999',
                    'status': 'denied',
                    'attempts_count': 1
                })()
            )
        result = self.security.monitor_failed_attempts(self.user_id, 60)
        assert result['is_suspicious'] is True
        assert result['attempts_count'] == 5

    def test_monitor_passed_attempts(self):
        now = datetime.now()
        for i in range(2):
            past_time = (now - timedelta(minutes=i*5)).strftime("%Y-%m-%d %H:%M:%S")
            self.db.create_access_log(
                type('Log', (), {
                    'user_id': self.user_id,
                    'access_time': past_time,
                    'location': 'Room 101',
                    'status': 'granted',
                    'attempts_count': 1
                })()
            )
        result = self.security.monitor_failed_attempts(self.user_id, 60)
        assert result['is_suspicious'] is False
        assert result['attempts_count'] == 0


class TestEventListeners:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.db_path = "test_listeners.db"
        self.db = DatabaseManager(self.db_path)
        self.db.init_db()
        self.dispatcher = EventDispatcher()
        self.security = SecurityManager(self.db, self.dispatcher)

        self.user_id = self.db.create_user(
            type('User', (), {'name': 'John', 'department': 'IT', 'access_level': 3, 'assigned_room': 'Room 101'})()
        )

        self.dispatcher.register_listener('on_suspicious_behavior', self.security.on_suspicious_behavior_handler)
        self.dispatcher.register_listener('on_access_denied', self.security.on_access_denied_handler)
        self.dispatcher.register_listener('on_multiple_attempts', self.security.on_multiple_attempts_handler)

        yield
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_on_suspicious_behavior_handler(self):
        event_args = SuspiciousBehaviorEventArgs(
            user_id=self.user_id,
            score=0.8,
            reason='Night access',
            timestamp='2024-01-15 02:00:00'
        )
        self.dispatcher.dispatch_event('on_suspicious_behavior', event_args)
        alerts = self.db.get_user_alerts(self.user_id)
        assert len(alerts) == 1

    def test_on_access_denied_handler(self):
        event_args = AccessEventArgs(
            user_id=self.user_id,
            location='Room 999',
            reason='Not authorized',
            timestamp='2024-01-15 09:30:00'
        )
        self.dispatcher.dispatch_event('on_access_denied', event_args)
        alerts = self.db.get_user_alerts(self.user_id)
        assert len(alerts) == 1
        assert alerts[0].alert_type == 'access_denied'

    def test_on_multiple_attempts_handler(self):
        event_args = AlertEventArgs(
            user_id=self.user_id,
            alert_type='multiple_attempts',
            description='5 failed attempts',
            created_at='2024-01-15 09:30:00'
        )
        self.dispatcher.dispatch_event('on_multiple_attempts', event_args)
        alerts = self.db.get_user_alerts(self.user_id)
        assert len(alerts) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])