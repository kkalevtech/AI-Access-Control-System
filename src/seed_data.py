import random
import sqlite3

from src.database.database_manager import DatabaseManager
from src.models import User, AccessLog, Department, Room


ROOM_SUFFIXES = ['101', '102', '201', '202', '301', '302']
DEPARTMENT_NAMES = ['Finance', 'HR', 'IT', 'Marketing', 'Operations']


def random_time():
    return f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"


def generate_messy_data(db_path="access_control.db"):
    random.seed(42)

    import os
    if os.path.exists(db_path):
        os.remove(db_path)

    db = DatabaseManager(db_path)
    db.init_db()

    depts = {}
    for name in DEPARTMENT_NAMES:
        dept = Department(name=name)
        dept.id = db.create_department(dept)
        depts[name] = dept

    rooms_by_code = {}
    for dept_name in DEPARTMENT_NAMES:
        prefix = dept_name[:3].upper()
        for suffix in ROOM_SUFFIXES:
            code = f"{prefix}-{suffix}"
            room = Room(room_code=code, department_id=depts[dept_name].id)
            room.id = db.create_room(room)
            rooms_by_code[code] = room

    names = [
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
        "Ivy", "Jack", "Karen", "Leo", "Maria", "Nathan", "Olivia", "Paul",
        "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xander",
        "Yara", "Zack", "Amy", "Ben", "Carla", "Dan"
    ]

    users = []
    for name in names:
        dept_name = random.choice(DEPARTMENT_NAMES)
        dept_rooms = [code for code in rooms_by_code if code.startswith(dept_name[:3].upper())]
        room_code = random.choice(dept_rooms)
        room = rooms_by_code[room_code]
        level = random.randint(1, 5)

        user = User(
            name=name,
            department=dept_name,
            access_level=level,
            assigned_room=room_code,
            assigned_room_id=room.id
        )
        user.id = db.create_user(user)
        users.append(user)

    all_room_codes = list(rooms_by_code.keys())

    for _ in range(300):
        user = random.choice(users)
        dept_prefix = user.department[:3].upper()

        if random.random() > 0.4:
            room_code = user.assigned_room
        else:
            room_code = random.choice(all_room_codes)

        room = rooms_by_code[room_code]

        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        access_time = f"{hour:02d}:{minute:02d}:{second:02d}"
        is_weekend = 1 if random.random() < 0.3 else 0

        if room_code == user.assigned_room:
            status = 'granted' if random.random() > 0.1 else 'denied'
        else:
            status = 'granted' if random.random() > 0.6 else 'denied'

        db.create_access_log(AccessLog(
            user_id=user.id,
            access_time=access_time,
            is_weekend=is_weekend,
            location=room_code,
            room_id=room.id,
            status=status
        ))

    patterns = [
        (random.choice(users), 'ex-employee', 5, 'granted'),
        (random.choice(users), 'night-shift', 10, 'granted'),
        (random.choice(users), 'denied-always', 8, 'denied'),
        (random.choice(users), 'favor-granted', 10, 'granted'),
        (random.choice(users), 'friend-override', 6, 'granted'),
    ]

    for user, pattern_type, count, base_status in patterns:
        for i in range(count):
            hour = random.randint(9, 18)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)

            if pattern_type == 'night-shift':
                hour = random.randint(22, 23) if i % 2 == 0 else random.randint(0, 4)

            access_time = f"{hour:02d}:{minute:02d}:{second:02d}"
            is_weekend = 1 if random.random() < 0.3 else 0
            room_code = user.assigned_room
            room = rooms_by_code[room_code]
            status = base_status

            db.create_access_log(AccessLog(
                user_id=user.id,
                access_time=access_time,
                is_weekend=is_weekend,
                location=room_code,
                room_id=room.id,
                status=status
            ))

    db.close()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM access_logs")
    logs_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM departments")
    depts_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM rooms")
    rooms_count = cur.fetchone()[0]

    print(f"[OK] Generated: {depts_count} departments, {rooms_count} rooms, {users_count} users, {logs_count} logs")

    print("\n=== SAMPLE ===")
    cur.execute('''
        SELECT al.id, u.name, al.location, al.status, al.access_time
        FROM access_logs al
        JOIN users u ON al.user_id = u.id
        ORDER BY al.id
        LIMIT 15
    ''')
    for row in cur.fetchall():
        print(f"ID:{row[0]:>3} {row[1]:<10} -> {row[2]:<10} [{row[3]:<7}] {row[4][:10]}")

    conn.close()


if __name__ == "__main__":
    generate_messy_data("access_control.db")
