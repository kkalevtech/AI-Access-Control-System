class AccessLog:
    def __init__(self, id=None, user_id=None, access_time=None, location=None, status='granted'):
        self.id = id
        self.user_id = user_id
        self.access_time = access_time
        self.location = location
        self.status = status

    def __repr__(self):
        return f'AccessLog(id={self.id}, user_id={self.user_id}, access_time="{self.access_time}", location="{self.location}", status="{self.status}")'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'access_time': self.access_time,
            'location': self.location,
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            access_time=data.get('access_time'),
            location=data.get('location'),
            status=data.get('status', 'granted')
        )