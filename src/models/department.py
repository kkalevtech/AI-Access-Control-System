class Department:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        return f'Department(id={self.id}, name="{self.name}")'

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    @classmethod
    def from_dict(cls, data):
        return cls(id=data.get('id'), name=data.get('name'))
