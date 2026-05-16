class Room:
    def __init__(self, id=None, room_code=None, department_id=None, department_name=None):
        self.id = id
        self.room_code = room_code
        self.department_id = department_id
        self.department_name = department_name

    def __repr__(self):
        return f'Room(id={self.id}, room_code="{self.room_code}", department_id={self.department_id})'

    def to_dict(self):
        return {
            'id': self.id,
            'room_code': self.room_code,
            'department_id': self.department_id,
            'department_name': self.department_name
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            room_code=data.get('room_code'),
            department_id=data.get('department_id'),
            department_name=data.get('department_name')
        )
