from datetime import datetime, timedelta
import random

from src.database.database_manager import DatabaseManager
from src.models import User, AccessLog


DEPARTMENTS = ['IT', 'HR', 'Finance', 'Marketing', 'Operations']
ROOMS = ['IT-101', 'IT-102', 'HR-201', 'HR-202', 'FIN-301', 'FIN-302', 'MKT-401', 'OPS-501']


def generate_sample_data(db_path="access_control.db"):
    db = DatabaseManager(db_path)
    db.init_db()

    users = []
    for i, name in enumerate(['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince', 'Eve Wilson',
                           'Frank Miller', 'Grace Lee', 'Henry Chen', 'Ivy Martinez', 'Jack Davis',
                           'Karen White', 'Leo Garcia', 'Maria Rodriguez', 'Nathan Kim', 'Olivia Taylor',
                           'Paul Anderson', 'Quinn Thomas', 'Rachel Moore', 'Sam Jackson', 'Tina Harris'], 
                           start=1):
        dept = random.choice(DEPARTMENTS)
        access_level = random.randint(1, 5)
        assigned_room = f"{dept}-{random.randint(1, 5) * 101}"
        user = User(name=name, department=dept, access_level=access_level, assigned_room=assigned_room)
        user.id = db.create_user(user)
        users.append(user)

    now = datetime.now()
    access_logs = []

    for i in range(120):
        user = random.choice(users)
        access_time = now - timedelta(
            hours=random.randint(0, 500),
            minutes=random.randint(0, 59)
        )

        is_night = access_time.hour >= 22 or access_time.hour < 6
        is_high_frequency = random.random() < 0.1
        is_wrong_room = random.random() < 0.15

        if is_night or is_high_frequency or is_wrong_room:
            if is_wrong_room:
                other_rooms = [r for r in ROOMS if r != user.assigned_room]
                location = random.choice(other_rooms) if other_rooms else random.choice(ROOMS)
            else:
                location = user.assigned_room
            status = 'denied' if (is_night and random.random() < 0.7) or (is_wrong_room and random.random() < 0.5) else 'granted'
        else:
            location = user.assigned_room if random.random() < 0.7 else random.choice(ROOMS)
            status = 'granted' if random.random() < 0.85 else 'denied'

        log = AccessLog(
            user_id=user.id,
            access_time=access_time.isoformat(),
            location=location,
            status=status,
            attempts_count=1
        )
        log.id = db.create_access_log(log)
        access_logs.append(log)

    db.close()
    return {'users': len(users), 'access_logs': len(access_logs)}


if __name__ == "__main__":
    result = generate_sample_data()
    print(f"Generated {result['users']} users and {result['access_logs']} access logs")