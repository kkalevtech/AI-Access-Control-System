from datetime import datetime, timedelta
from src.models import AccessLog
from src.events import AlertEventArgs, SuspiciousBehaviorEventArgs


class SecurityManager:
    def __init__(self, database, event_dispatcher, file_manager=None):
        self.database = database
        self.event_dispatcher = event_dispatcher
        self.file_manager = file_manager

    def monitor_failed_attempts(self, user_id, time_window_minutes=60):
        all_logs = self.database.get_user_access_logs(user_id)
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')

        cutoff_seconds = (now.hour * 3600 + now.minute * 60 + now.second) - time_window_minutes * 60
        if cutoff_seconds < 0:
            cutoff_seconds += 86400
        cutoff_hour = cutoff_seconds // 3600
        cutoff_min = (cutoff_seconds % 3600) // 60
        cutoff_sec = cutoff_seconds % 60
        cutoff_time = f"{cutoff_hour:02d}:{cutoff_min:02d}:{cutoff_sec:02d}"

        recent_denied = []
        for log in all_logs:
            try:
                if log.status == 'denied':
                    if cutoff_time <= current_time:
                        if cutoff_time <= log.access_time <= current_time:
                            recent_denied.append(log)
                    else:
                        if log.access_time >= cutoff_time or log.access_time <= current_time:
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
                created_at=datetime.now().strftime("%H:%M:%S")
            )
            self.event_dispatcher.dispatch_event('on_multiple_attempts', event_args)

        return {
            'is_suspicious': is_suspicious,
            'attempts_count': attempts_count,
            'time_window': time_window_minutes
        }

    def on_suspicious_behavior_handler(self, event_args):
        if self.file_manager:
            self.file_manager.write_log(f"Suspicious behavior: User {event_args.user_id} - {event_args.reason}")

    def on_access_denied_handler(self, event_args):
        if self.file_manager:
            self.file_manager.write_log(f"Access denied to {event_args.location}: {event_args.reason}")

    def on_multiple_attempts_handler(self, event_args):
        if self.file_manager:
            self.file_manager.write_log(f"Multiple attempts: {event_args.description}")
