from datetime import datetime, timedelta
from src.models import Alert
from src.events import AlertEventArgs, SuspiciousBehaviorEventArgs


class SecurityManager:
    def __init__(self, database, event_dispatcher, file_manager=None):
        self.database = database
        self.event_dispatcher = event_dispatcher
        self.file_manager = file_manager

    def handle_alert(self, event_args):
        alert = Alert(
            user_id=event_args.user_id,
            alert_type=event_args.alert_type,
            description=event_args.description,
            created_at=event_args.created_at
        )
        self.database.create_alert(alert)
        if self.file_manager:
            self.file_manager.write_log(f"Alert: {event_args.alert_type} - {event_args.description}")

    def log_denied_access(self, user_id, location, reason, access_time):
        alert = Alert(
            user_id=user_id,
            alert_type='access_denied',
            description=f"Access denied to {location}: {reason}",
            created_at=access_time
        )
        self.database.create_alert(alert)

    def monitor_failed_attempts(self, user_id, time_window_minutes=60):
        all_logs = self.database.get_user_access_logs(user_id)
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)

        recent_denied = []
        for log in all_logs:
            try:
                log_time_str = log.access_time.replace('Z', '+00:00')
                if 'T' in log_time_str:
                    log_time = datetime.fromisoformat(log_time_str)
                else:
                    log_time = datetime.strptime(log_time_str, "%Y-%m-%d %H:%M:%S")
                if log.status == 'denied' and log_time > cutoff_time:
                    recent_denied.append(log)
            except (ValueError, AttributeError):
                continue

        attempts_count = len(recent_denied)
        is_suspicious = attempts_count > 3

        if is_suspicious:
            event_args = AlertEventArgs(
                user_id=user_id,
                alert_type='multiple_attempts',
                description=f'{attempts_count} failed attempts in {time_window_minutes} minutes',
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            self.event_dispatcher.dispatch_event('on_multiple_attempts', event_args)

        return {
            'is_suspicious': is_suspicious,
            'attempts_count': attempts_count,
            'time_window': time_window_minutes
        }

    def on_suspicious_behavior_handler(self, event_args):
        if isinstance(event_args, SuspiciousBehaviorEventArgs):
            alert = Alert(
                user_id=event_args.user_id,
                alert_type='suspicious_behavior',
                description=f"Suspicious behavior detected: {event_args.reason} (score: {event_args.score})",
                created_at=event_args.timestamp
            )
            self.database.create_alert(alert)
            if self.file_manager:
                self.file_manager.write_log(f"Suspicious behavior: User {event_args.user_id} - {event_args.reason}")
        elif hasattr(event_args, 'user_id'):
            alert = Alert(
                user_id=event_args.user_id,
                alert_type='suspicious_behavior',
                description=f"Suspicious behavior detected: {getattr(event_args, 'reason', 'Unknown')}",
                created_at=getattr(event_args, 'timestamp', datetime.now().isoformat())
            )
            self.database.create_alert(alert)
            if self.file_manager:
                self.file_manager.write_log(f"Suspicious behavior: User {event_args.user_id}")

    def on_access_denied_handler(self, event_args):
        self.log_denied_access(
            event_args.user_id,
            event_args.location,
            event_args.reason,
            event_args.timestamp
        )

    def on_multiple_attempts_handler(self, event_args):
        alert = Alert(
            user_id=event_args.user_id,
            alert_type='multiple_attempts',
            description=event_args.description,
            created_at=event_args.created_at
        )
        self.database.create_alert(alert)