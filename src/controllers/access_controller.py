from datetime import datetime
from src.models import AccessLog
from src.events import AccessEventArgs, SuspiciousBehaviorEventArgs
from src.ai.analyzer import BehaviorAnalyzer


class AccessController:
    def __init__(self, database, event_dispatcher):
        self.database = database
        self.event_dispatcher = event_dispatcher
        self.analyzer = BehaviorAnalyzer(database)

    def request_access(self, user_id, location, access_time=None):
        if access_time is None:
            access_time = datetime.now().isoformat()

        if not isinstance(access_time, str):
            access_time = access_time.isoformat()

        user = self.database.get_user(user_id)
        if not user:
            return {
                'granted': False,
                'classification': 'Unknown',
                'confidence_normal': 0,
                'confidence_suspicious': 0,
                'reason': 'User not found',
                'user_id': user_id,
                'location': location,
                'timestamp': access_time
            }

        if self.analyzer.is_trained:
            analysis = self.analyzer.analyze(user_id, access_time, location)

            if 'error' in analysis:
                return self._process_basic_access(user, location, access_time)

            classification = analysis['classification']
            confidence_suspicious = analysis.get('confidence_suspicious', 0)

            if classification == "Suspicious":
                self.event_dispatcher.dispatch_event('on_suspicious_behavior', SuspiciousBehaviorEventArgs(
                    user_id=user_id,
                    score=confidence_suspicious,
                    reason=analysis.get('reason', 'Suspicious behavior detected'),
                    timestamp=access_time
                ))
                deny_result = self.deny_access(user_id, location, analysis.get('reason', 'Suspicious behavior detected'), access_time)
                deny_result['classification'] = classification
                deny_result['confidence_normal'] = analysis.get('confidence_normal', 0)
                deny_result['confidence_suspicious'] = confidence_suspicious
                return deny_result

            return self.grant_access_with_analysis(user_id, location, access_time, analysis)
        else:
            return self._process_basic_access(user, location, access_time)

    def _process_basic_access(self, user, location, access_time):
        if user.assigned_room and location == user.assigned_room:
            return self.grant_access(user_id=user.id, location=location, access_time=access_time)
        elif user.department and location.startswith(user.department):
            return self.grant_access(user_id=user.id, location=location, access_time=access_time)
        else:
            reason = f"Location {location} not authorized for user"
            return self.deny_access(user_id=user.id, location=location, reason=reason, access_time=access_time)

    def grant_access_with_analysis(self, user_id, location, access_time, analysis):
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
            'classification': analysis.get('classification', 'Normal'),
            'confidence_normal': analysis.get('confidence_normal', 0),
            'confidence_suspicious': analysis.get('confidence_suspicious', 0),
            'reason': analysis.get('reason', 'Access granted'),
            'user_id': user_id,
            'location': location,
            'timestamp': access_time
        }

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
            'classification': 'Normal',
            'confidence_normal': 100,
            'confidence_suspicious': 0,
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