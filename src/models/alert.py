class Alert:
    def __init__(self, id=None, user_id=None, alert_type=None, description=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.alert_type = alert_type
        self.description = description
        self.created_at = created_at

    def __repr__(self):
        return f'Alert(id={self.id}, user_id={self.user_id}, alert_type="{self.alert_type}", description="{self.description}", created_at="{self.created_at}")'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'alert_type': self.alert_type,
            'description': self.description,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            alert_type=data.get('alert_type'),
            description=data.get('description'),
            created_at=data.get('created_at')
        )