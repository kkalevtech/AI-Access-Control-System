class User:
    def __init__(self, id=None, name=None, role=None, access_level=1,
                 assigned_room=None, assigned_room_id=None, departments=None):
        self.id = id
        self.name = name
        self.role = role
        self.access_level = access_level
        self.assigned_room = assigned_room
        self.assigned_room_id = assigned_room_id
        self.departments = departments or []

    def __repr__(self):
        return f'User(id={self.id}, name="{self.name}", role="{self.role}", access_level={self.access_level}, assigned_room="{self.assigned_room}")'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'access_level': self.access_level,
            'assigned_room': self.assigned_room,
            'assigned_room_id': self.assigned_room_id,
            'departments': self.departments
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            role=data.get('role'),
            access_level=data.get('access_level', 1),
            assigned_room=data.get('assigned_room'),
            assigned_room_id=data.get('assigned_room_id'),
            departments=data.get('departments', [])
        )
