import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.events import EventDispatcher, AccessEventArgs, AlertEventArgs, SuspiciousBehaviorEventArgs


class TestAccessEventArgs:
    def test_creation(self):
        args = AccessEventArgs(user_id=1, location="Room 101", reason="Access granted", timestamp="2024-01-15 09:30:00")
        assert args.user_id == 1
        assert args.location == "Room 101"
        assert args.reason == "Access granted"
        assert args.timestamp == "2024-01-15 09:30:00"

    def test_to_dict(self):
        args = AccessEventArgs(user_id=1, location="Room 101", reason="Access denied", timestamp="2024-01-15 09:30:00")
        d = args.to_dict()
        assert d['user_id'] == 1
        assert d['location'] == "Room 101"
        assert d['reason'] == "Access denied"


class TestAlertEventArgs:
    def test_creation(self):
        args = AlertEventArgs(user_id=1, alert_type="suspicious_behavior", description="Multiple failed attempts", created_at="2024-01-15 09:30:00")
        assert args.user_id == 1
        assert args.alert_type == "suspicious_behavior"
        assert args.description == "Multiple failed attempts"

    def test_to_dict(self):
        args = AlertEventArgs(user_id=1, alert_type="access_denied", description="Test", created_at="2024-01-15 09:30:00")
        d = args.to_dict()
        assert d['alert_type'] == "access_denied"


class TestSuspiciousBehaviorEventArgs:
    def test_creation(self):
        args = SuspiciousBehaviorEventArgs(user_id=1, score=0.85, reason="Night access", timestamp="2024-01-15 02:00:00")
        assert args.user_id == 1
        assert args.score == 0.85
        assert args.reason == "Night access"

    def test_to_dict(self):
        args = SuspiciousBehaviorEventArgs(user_id=1, score=0.75, reason="High frequency", timestamp="2024-01-15 09:30:00")
        d = args.to_dict()
        assert d['score'] == 0.75


class TestEventDispatcher:
    def test_register_listener(self):
        dispatcher = EventDispatcher()
        calls = []

        def callback(args):
            calls.append(args)

        dispatcher.register_listener("on_access_denied", callback)
        listeners = dispatcher.get_listeners("on_access_denied")
        assert len(listeners) == 1

    def test_unregister_listener(self):
        dispatcher = EventDispatcher()

        def callback(args):
            pass

        dispatcher.register_listener("on_access_denied", callback)
        dispatcher.unregister_listener("on_access_denied", callback)
        listeners = dispatcher.get_listeners("on_access_denied")
        assert len(listeners) == 0

    def test_dispatch_event_single_listener(self):
        dispatcher = EventDispatcher()
        received = []

        def callback(args):
            received.append(args)

        dispatcher.register_listener("on_suspicious_behavior", callback)
        event_args = SuspiciousBehaviorEventArgs(user_id=1, score=0.8, reason="Test", timestamp="2024-01-15 09:30:00")
        dispatcher.dispatch_event("on_suspicious_behavior", event_args)

        assert len(received) == 1
        assert received[0].user_id == 1

    def test_dispatch_event_multiple_listeners(self):
        dispatcher = EventDispatcher()
        received1 = []
        received2 = []

        def callback1(args):
            received1.append(args)

        def callback2(args):
            received2.append(args)

        dispatcher.register_listener("on_suspicious_behavior", callback1)
        dispatcher.register_listener("on_suspicious_behavior", callback2)
        event_args = SuspiciousBehaviorEventArgs(user_id=1, score=0.8, reason="Test", timestamp="2024-01-15 09:30:00")
        dispatcher.dispatch_event("on_suspicious_behavior", event_args)

        assert len(received1) == 1
        assert len(received2) == 1

    def test_multiple_listeners_for_event_type(self):
        dispatcher = EventDispatcher()
        calls = []

        def callback1(args):
            calls.append(1)

        def callback2(args):
            calls.append(2)

        dispatcher.register_listener("on_access_denied", callback1)
        dispatcher.register_listener("on_access_denied", callback2)
        event_args = AccessEventArgs(user_id=1, location="Room 101", reason="Test", timestamp="2024-01-15 09:30:00")
        dispatcher.dispatch_event("on_access_denied", event_args)

        assert len(calls) == 2
        assert 1 in calls
        assert 2 in calls


if __name__ == "__main__":
    pytest.main([__file__, "-v"])