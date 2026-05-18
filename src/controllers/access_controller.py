from datetime import datetime
from src.models import AccessLog
from src.events import AccessEventArgs, SuspiciousBehaviorEventArgs
from src.ai.analyzer import BehaviorAnalyzer, DEPT_PREFIX_MAP


class AccessController:
    def __init__(self, database, event_dispatcher, analyzer=None):
        self.database = database
        self.event_dispatcher = event_dispatcher
        self.analyzer = analyzer if analyzer is not None else BehaviorAnalyzer(database)

    def _now_time(self):
        now = datetime.now()
        return now.strftime('%H:%M:%S'), 1 if now.weekday() >= 5 else 0

    def request_access(self, user_id, location, access_time=None):
        if access_time is None:
            access_time, is_weekend = self._now_time()
        else:
            is_weekend = 1 if datetime.now().weekday() >= 5 else 0

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
                'timestamp': access_time,
                'is_weekend': is_weekend
            }

        if self.analyzer.is_trained:
            analysis = self.analyzer.analyze(user_id, access_time, location, is_weekend)

            if 'error' in analysis:
                return self._process_request(user, location, access_time, is_weekend)

            classification = analysis['classification']
            confidence_suspicious = analysis.get('confidence_suspicious', 0)

            if classification == "Suspicious":
                reason = analysis.get('reason', 'Suspicious behavior detected')
                self.event_dispatcher.dispatch_event('on_suspicious_behavior', SuspiciousBehaviorEventArgs(
                    user_id=user_id,
                    score=confidence_suspicious,
                    reason=reason,
                    timestamp=access_time
                ))
                self.event_dispatcher.dispatch_event('on_access_denied', AccessEventArgs(
                    user_id=user_id,
                    location=location,
                    reason=reason,
                    timestamp=access_time
                ))
                return {
                    'granted': False,
                    'classification': classification,
                    'confidence_normal': analysis.get('confidence_normal', 0),
                    'confidence_suspicious': confidence_suspicious,
                    'reason': reason,
                    'user_id': user_id,
                    'location': location,
                    'timestamp': access_time,
                    'is_weekend': is_weekend
                }

            return {
                'granted': True,
                'classification': classification,
                'confidence_normal': analysis.get('confidence_normal', 0),
                'confidence_suspicious': confidence_suspicious,
                'reason': analysis.get('reason', 'Access granted'),
                'user_id': user_id,
                'location': location,
                'timestamp': access_time,
                'is_weekend': is_weekend
            }
        else:
            return self._process_request(user, location, access_time, is_weekend)

    def _process_request(self, user, location, access_time, is_weekend=0):
        if user.assigned_room and location == user.assigned_room:
            return {
                'granted': True,
                'classification': 'Normal',
                'confidence_normal': 100,
                'confidence_suspicious': 0,
                'reason': 'Access granted',
                'user_id': user.id,
                'location': location,
                'timestamp': access_time,
                'is_weekend': is_weekend
            }

        if user.departments:
            loc_prefix = location.split('-')[0] if '-' in location else location
            loc_dept = DEPT_PREFIX_MAP.get(loc_prefix, '')
            if loc_dept in user.departments:
                return {
                    'granted': True,
                    'classification': 'Normal',
                    'confidence_normal': 100,
                    'confidence_suspicious': 0,
                    'reason': 'Access granted',
                    'user_id': user.id,
                    'location': location,
                    'timestamp': access_time,
                    'is_weekend': is_weekend
                }

        reason = f"Location {location} not authorized for user"
        self.event_dispatcher.dispatch_event('on_access_denied', AccessEventArgs(
            user_id=user.id,
            location=location,
            reason=reason,
            timestamp=access_time
        ))
        return {
            'granted': False,
            'reason': reason,
            'user_id': user.id,
            'location': location,
            'timestamp': access_time,
            'is_weekend': is_weekend
        }

    def grant_access_with_analysis(self, user_id, location, access_time, analysis, is_weekend=0):
        log = AccessLog(
            user_id=user_id,
            access_time=access_time,
            is_weekend=is_weekend,
            location=location,
            status='granted'
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
            'timestamp': access_time,
            'is_weekend': is_weekend
        }

    def grant_access(self, user_id, location, access_time, is_weekend=0):
        log = AccessLog(
            user_id=user_id,
            access_time=access_time,
            is_weekend=is_weekend,
            location=location,
            status='granted'
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
            'timestamp': access_time,
            'is_weekend': is_weekend
        }

    def deny_access(self, user_id, location, reason, access_time, is_weekend=0):
        log = AccessLog(
            user_id=user_id,
            access_time=access_time,
            is_weekend=is_weekend,
            location=location,
            status='denied'
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
            'timestamp': access_time,
            'is_weekend': is_weekend
        }
