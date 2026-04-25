class AccessEventArgs:
    def __init__(self, user_id, location, reason, timestamp):
        self.user_id = user_id
        self.location = location
        self.reason = reason
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'location': self.location,
            'reason': self.reason,
            'timestamp': self.timestamp
        }


class AlertEventArgs:
    def __init__(self, user_id, alert_type, description, created_at):
        self.user_id = user_id
        self.alert_type = alert_type
        self.description = description
        self.created_at = created_at

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'alert_type': self.alert_type,
            'description': self.description,
            'created_at': self.created_at
        }


class SuspiciousBehaviorEventArgs:
    def __init__(self, user_id, score, reason, timestamp):
        self.user_id = user_id
        self.score = score
        self.reason = reason
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'score': self.score,
            'reason': self.reason,
            'timestamp': self.timestamp
        }