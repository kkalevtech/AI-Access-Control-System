class AccessLog:
    def __init__(self, id=None, user_id=None, access_time=None, is_weekend=0,
                 location=None, status='granted', room_id=None):
        self.id = id
        self.user_id = user_id
        self.access_time = access_time
        self.is_weekend = is_weekend
        self.location = location
        self.status = status
        self.room_id = room_id

    def __repr__(self):
        return f'AccessLog(id={self.id}, user_id={self.user_id}, access_time="{self.access_time}", is_weekend={self.is_weekend}, location="{self.location}", status="{self.status}")'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'access_time': self.access_time,
            'is_weekend': self.is_weekend,
            'location': self.location,
            'status': self.status,
            'room_id': self.room_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            access_time=data.get('access_time'),
            is_weekend=data.get('is_weekend', 0),
            location=data.get('location'),
            status=data.get('status', 'granted'),
            room_id=data.get('room_id')
        )
