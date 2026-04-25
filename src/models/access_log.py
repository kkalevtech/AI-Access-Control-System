class AccessLog:
    def __init__(self, id=None, user_id=None, access_time=None, location=None, status='granted', attempts_count=1):
        self.id = id
        self.user_id = user_id
        self.access_time = access_time
        self.location = location
        self.status = status
        self.attempts_count = attempts_count

    def __repr__(self):
        return f'AccessLog(id={self.id}, user_id={self.user_id}, access_time="{self.access_time}", location="{self.location}", status="{self.status}", attempts_count={self.attempts_count})'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'access_time': self.access_time,
            'location': self.location,
            'status': self.status,
            'attempts_count': self.attempts_count
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            access_time=data.get('access_time'),
            location=data.get('location'),
            status=data.get('status', 'granted'),
            attempts_count=data.get('attempts_count', 1)
        )