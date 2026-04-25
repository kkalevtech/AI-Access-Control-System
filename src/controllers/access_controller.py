from datetime import datetime
from src.models import AccessLog
from src.events import AccessEventArgs


class AccessController:
    def __init__(self, database, event_dispatcher):
        self.database = database
        self.event_dispatcher = event_dispatcher

    def request_access(self, user_id, location, access_time=None):
        if access_time is None:
            access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user = self.database.get_user(user_id)
        if not user:
            return {
                'granted': False,
                'reason': 'User not found',
                'user_id': user_id,
                'location': location,
                'timestamp': access_time
            }

        if user.assigned_room and location == user.assigned_room:
            return self.grant_access(user_id, location, access_time)
        elif user.department and location.startswith(user.department):
            return self.grant_access(user_id, location, access_time)
        else:
            reason = f"Location {location} not authorized for user"
            return self.deny_access(user_id, location, reason, access_time)

    def grant_access(self, user_id, location, access_time):
        log = AccessLog(
            user_id=user_id,
            access_time=access_time,
            location=location,
            status='granted',
            attempts_count=1
        )
        self.database.create_access_log(log)
        return {
            'granted': True,
            'reason': 'Access granted',
            'user_id': user_id,
            'location': location,
            'timestamp': access_time
        }

    def deny_access(self, user_id, location, reason, access_time):
        log = AccessLog(
            user_id=user_id,
            access_time=access_time,
            location=location,
            status='denied',
            attempts_count=1
        )
        self.database.create_access_log(log)

        event_args = AccessEventArgs(
            user_id=user_id,
            location=location,
            reason=reason,
            timestamp=access_time
        )
        self.event_dispatcher.dispatch_event('on_access_denied', event_args)

        return {
            'granted': False,
            'reason': reason,
            'user_id': user_id,
            'location': location,
            'timestamp': access_time
        }