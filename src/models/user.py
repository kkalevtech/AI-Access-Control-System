class User:
    def __init__(self, id=None, name=None, department=None, access_level=1, assigned_room=None):
        self.id = id
        self.name = name
        self.department = department
        self.access_level = access_level
        self.assigned_room = assigned_room

    def __repr__(self):
        return f'User(id={self.id}, name="{self.name}", department="{self.department}", access_level={self.access_level}, assigned_room="{self.assigned_room}")'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'department': self.department,
            'access_level': self.access_level,
            'assigned_room': self.assigned_room
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            department=data.get('department'),
            access_level=data.get('access_level', 1),
            assigned_room=data.get('assigned_room')
        )