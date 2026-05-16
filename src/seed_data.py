import random
random.seed(42)
from src.database.database_manager import DatabaseManager
from src.models import User, AccessLog, Department, Room


DEPARTMENTS = ['Finance', 'HR', 'IT', 'Marketing', 'Operations']
ROOM_SUFFIXES = ['101', '102', '201', '202', '301', '302']
DEPT_PREFIX = {
    'Finance': 'FIN', 'HR': 'HR', 'IT': 'IT',
    'Marketing': 'MKT', 'Operations': 'OPS'
}


def _build_log(user_id, time_str, is_weekend, location, status):
    return AccessLog(
        user_id=user_id,
        access_time=time_str,
        is_weekend=is_weekend,
        location=location,
        status=status
    )


def generate_messy_data(db_path="access_control.db", db=None):
    _external_db = db is not None
    if db is None:
        import os
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except PermissionError:
            pass
        db = DatabaseManager(db_path)
        db.init_db()
        # Clear any leftover data if deletion failed
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            cursor.execute("DELETE FROM access_logs")
            cursor.execute("DELETE FROM user_departments")
            cursor.execute("DELETE FROM users")
            cursor.execute("DELETE FROM rooms")
            cursor.execute("DELETE FROM departments")
            db.connection.commit()

    # --- Create departments ---
    dept_map = {}
    for name in DEPARTMENTS:
        dept = Department(name=name)
        dept.id = db.create_department(dept)
        dept_map[name] = dept

    # --- Create rooms ---
    rooms_by_code = {}
    for dept_name in DEPARTMENTS:
        prefix = DEPT_PREFIX[dept_name]
        for suffix in ROOM_SUFFIXES:
            code = f"{prefix}-{suffix}"
            room = Room(room_code=code, department_id=dept_map[dept_name].id)
            room.id = db.create_room(room)
            rooms_by_code[code] = room

    # ===================================================================
    # USER DEFINITIONS
    # ===================================================================
    # Each: (name, role, access_level, assigned_room, [departments])
    user_defs = [
        ("Alice Anderson",  "Finance Director",       5, "FIN-201", ["Finance"]),
        ("Bob Brown",       "IT Security Admin",       5, "IT-301",  ["IT"]),
        ("Carol Chen",      "HR Manager",              4, "HR-201",  ["HR"]),
        ("David Davis",     "Night Security Guard",    3, "OPS-101", ["Operations"]),
        ("Eve Edwards",     "Marketing Lead",          4, "MKT-201", ["Marketing"]),
        ("Frank Foster",    "Finance Intern",          1, None,      ["Finance"]),
        ("Grace Garcia",    "Operations Supervisor",   3, "OPS-202", ["Operations"]),
        ("Henry Harris",    "Ex-Employee (Deactivated)", 1, "IT-101", ["IT"]),
        ("Iris Huang",      "Cross-Dept Coordinator",  3, "FIN-301", ["Finance", "HR", "Operations"]),
        ("Jack Johnson",    "Suspicious Outsider",     1, None,      []),
        ("Karen Kim",       "Executive Assistant",     4, "FIN-101", ["Finance", "IT", "Marketing", "HR", "Operations"]),
        ("Leo Lopez",       "Cleaner / Maintenance",   2, "OPS-302", ["Operations"]),
        ("Maria Martinez",  "Senior Developer",        4, "IT-202",  ["IT"]),
        ("Nathan Nguyen",   "New Marketing Hire",      1, "MKT-101", ["Marketing"]),
        ("Olivia Owens",    "CEO",                     5, "FIN-101", ["Finance", "IT", "Marketing", "HR", "Operations"]),
        ("Paul Patel",      "Part-Time Consultant",    2, "IT-102",  ["IT", "Marketing"]),
        ("Quinn Chen",      "Weekend IT Support",      3, "IT-101",  ["IT"]),
        ("Rachel Robinson", "Night Finance Auditor",   3, "FIN-102", ["Finance"]),
        ("Sam Stevens",     "Brute Force Simulator",   1, None,      []),
        ("Tina Turner",     "Department Hopper",       2, "MKT-301", ["Marketing"]),
    ]

    users = []
    for name, role, level, room, depts in user_defs:
        room_id = rooms_by_code[room].id if room else None
        user = User(
            name=name, role=role, access_level=level,
            assigned_room=room, assigned_room_id=room_id
        )
        user.id = db.create_user(user)
        dept_ids = [dept_map[d].id for d in depts if d in dept_map]
        db.set_user_departments(user.id, dept_ids)
        users.append(user)

    # Index users by name for log creation
    by_name = {}
    for u in users:
        by_name[u.name] = u

    # ===================================================================
    # 400 ACCESS LOGS (meticulously planned)
    # ===================================================================
    logs = []

    def al(user_name, time_str, is_weekend, location, status):
        u = by_name[user_name]
        logs.append((u.id, time_str, is_weekend, location, status))

    # --- 1. Alice Anderson (20 logs) ---
    al("Alice Anderson", "09:00:00", 0, "FIN-201", "granted")
    al("Alice Anderson", "10:30:00", 0, "FIN-202", "granted")
    al("Alice Anderson", "11:15:00", 0, "FIN-101", "granted")
    al("Alice Anderson", "14:00:00", 0, "FIN-301", "granted")
    al("Alice Anderson", "08:15:00", 0, "FIN-201", "granted")
    al("Alice Anderson", "15:45:00", 0, "FIN-302", "granted")
    al("Alice Anderson", "12:30:00", 0, "FIN-201", "granted")
    al("Alice Anderson", "16:00:00", 0, "FIN-102", "granted")
    al("Alice Anderson", "09:30:00", 0, "FIN-201", "granted")
    al("Alice Anderson", "11:00:00", 0, "FIN-202", "granted")
    al("Alice Anderson", "13:15:00", 0, "FIN-301", "granted")
    al("Alice Anderson", "17:30:00", 0, "FIN-201", "granted")
    al("Alice Anderson", "08:00:00", 0, "FIN-101", "granted")
    al("Alice Anderson", "10:00:00", 0, "FIN-201", "granted")
    al("Alice Anderson", "14:30:00", 0, "FIN-201", "granted")
    al("Alice Anderson", "19:00:00", 0, "FIN-201", "granted")
    al("Alice Anderson", "09:00:00", 0, "HR-101",  "denied")
    al("Alice Anderson", "11:00:00", 0, "IT-101",  "denied")
    al("Alice Anderson", "02:30:00", 0, "FIN-201", "denied")
    al("Alice Anderson", "23:00:00", 0, "FIN-201", "denied")

    # --- 2. Bob Brown (20 logs) ---
    al("Bob Brown", "08:30:00", 0, "IT-301", "granted")
    al("Bob Brown", "10:00:00", 0, "IT-101", "granted")
    al("Bob Brown", "11:30:00", 0, "IT-202", "granted")
    al("Bob Brown", "14:00:00", 0, "IT-201", "granted")
    al("Bob Brown", "15:15:00", 0, "IT-301", "granted")
    al("Bob Brown", "09:00:00", 0, "IT-102", "granted")
    al("Bob Brown", "13:00:00", 0, "IT-202", "granted")
    al("Bob Brown", "16:30:00", 0, "IT-101", "granted")
    al("Bob Brown", "08:00:00", 0, "IT-301", "granted")
    al("Bob Brown", "10:30:00", 0, "IT-201", "granted")
    al("Bob Brown", "22:00:00", 0, "IT-301", "granted")
    al("Bob Brown", "23:30:00", 0, "IT-301", "granted")
    al("Bob Brown", "09:30:00", 0, "IT-101", "granted")
    al("Bob Brown", "14:30:00", 0, "IT-102", "granted")
    al("Bob Brown", "17:00:00", 0, "IT-202", "granted")
    al("Bob Brown", "21:00:00", 0, "IT-301", "granted")
    al("Bob Brown", "03:00:00", 0, "FIN-101", "denied")
    al("Bob Brown", "10:00:00", 0, "HR-201", "denied")
    al("Bob Brown", "08:30:00", 1, "IT-301", "granted")
    al("Bob Brown", "11:00:00", 1, "IT-101", "granted")

    # --- 3. Carol Chen (20 logs) ---
    al("Carol Chen", "09:00:00", 0, "HR-201", "granted")
    al("Carol Chen", "10:15:00", 0, "HR-101", "granted")
    al("Carol Chen", "11:30:00", 0, "HR-102", "granted")
    al("Carol Chen", "14:00:00", 0, "HR-301", "granted")
    al("Carol Chen", "15:30:00", 0, "HR-201", "granted")
    al("Carol Chen", "09:15:00", 0, "HR-201", "granted")
    al("Carol Chen", "10:00:00", 0, "HR-301", "granted")
    al("Carol Chen", "13:00:00", 0, "HR-102", "granted")
    al("Carol Chen", "16:00:00", 0, "HR-201", "granted")
    al("Carol Chen", "09:30:00", 0, "HR-101", "granted")
    al("Carol Chen", "11:00:00", 0, "HR-201", "granted")
    al("Carol Chen", "14:30:00", 0, "HR-202", "granted")
    al("Carol Chen", "17:00:00", 0, "HR-201", "granted")
    al("Carol Chen", "08:45:00", 0, "HR-101", "granted")
    al("Carol Chen", "12:00:00", 0, "HR-201", "granted")
    al("Carol Chen", "15:00:00", 0, "HR-301", "granted")
    al("Carol Chen", "09:00:00", 0, "IT-101", "denied")
    al("Carol Chen", "14:00:00", 0, "FIN-201", "denied")
    al("Carol Chen", "22:00:00", 0, "HR-201", "denied")
    al("Carol Chen", "10:00:00", 1, "HR-201", "denied")

    # --- 4. David Davis (20 logs) ---
    al("David Davis", "20:00:00", 0, "OPS-101", "granted")
    al("David Davis", "21:30:00", 0, "FIN-101", "granted")
    al("David Davis", "22:45:00", 0, "IT-301", "granted")
    al("David Davis", "00:15:00", 0, "HR-101", "granted")
    al("David Davis", "02:00:00", 0, "MKT-201", "granted")
    al("David Davis", "04:30:00", 0, "OPS-101", "granted")
    al("David Davis", "05:45:00", 0, "OPS-202", "granted")
    al("David Davis", "20:30:00", 0, "OPS-101", "granted")
    al("David Davis", "23:00:00", 0, "FIN-302", "granted")
    al("David Davis", "01:30:00", 0, "OPS-102", "granted")
    al("David Davis", "03:15:00", 0, "IT-101", "granted")
    al("David Davis", "06:00:00", 0, "OPS-101", "granted")
    al("David Davis", "21:00:00", 1, "OPS-101", "granted")
    al("David Davis", "23:30:00", 1, "MKT-101", "granted")
    al("David Davis", "02:00:00", 1, "HR-201", "granted")
    al("David Davis", "05:00:00", 1, "OPS-101", "granted")
    al("David Davis", "20:00:00", 0, "OPS-101", "granted")
    al("David Davis", "22:00:00", 0, "FIN-101", "granted")
    al("David Davis", "00:30:00", 0, "IT-202", "granted")
    al("David Davis", "04:00:00", 0, "OPS-301", "granted")

    # --- 5. Eve Edwards (20 logs) ---
    al("Eve Edwards", "09:00:00", 0, "MKT-201", "granted")
    al("Eve Edwards", "10:30:00", 0, "MKT-101", "granted")
    al("Eve Edwards", "11:45:00", 0, "MKT-202", "granted")
    al("Eve Edwards", "14:00:00", 0, "MKT-301", "granted")
    al("Eve Edwards", "15:30:00", 0, "MKT-201", "granted")
    al("Eve Edwards", "09:15:00", 0, "MKT-201", "granted")
    al("Eve Edwards", "10:00:00", 0, "MKT-301", "granted")
    al("Eve Edwards", "13:00:00", 0, "MKT-102", "granted")
    al("Eve Edwards", "16:00:00", 0, "MKT-201", "granted")
    al("Eve Edwards", "20:00:00", 0, "MKT-201", "granted")
    al("Eve Edwards", "21:30:00", 0, "MKT-202", "granted")
    al("Eve Edwards", "09:30:00", 0, "MKT-101", "granted")
    al("Eve Edwards", "14:00:00", 0, "MKT-201", "granted")
    al("Eve Edwards", "11:00:00", 0, "FIN-101", "denied")
    al("Eve Edwards", "15:00:00", 0, "IT-201", "denied")
    al("Eve Edwards", "03:00:00", 0, "MKT-201", "denied")
    al("Eve Edwards", "10:00:00", 1, "MKT-201", "granted")
    al("Eve Edwards", "14:00:00", 1, "MKT-101", "granted")
    al("Eve Edwards", "08:30:00", 0, "MKT-201", "granted")
    al("Eve Edwards", "17:00:00", 0, "MKT-201", "granted")

    # --- 6. Frank Foster (20 logs) ---
    al("Frank Foster", "09:00:00", 0, "FIN-101", "granted")
    al("Frank Foster", "10:00:00", 0, "FIN-102", "granted")
    al("Frank Foster", "11:00:00", 0, "FIN-101", "granted")
    al("Frank Foster", "14:00:00", 0, "FIN-102", "granted")
    al("Frank Foster", "09:30:00", 0, "FIN-101", "granted")
    al("Frank Foster", "10:30:00", 0, "FIN-202", "denied")
    al("Frank Foster", "11:00:00", 0, "FIN-301", "denied")
    al("Frank Foster", "15:00:00", 0, "FIN-201", "denied")
    al("Frank Foster", "09:00:00", 0, "FIN-101", "granted")
    al("Frank Foster", "10:00:00", 0, "FIN-302", "denied")
    al("Frank Foster", "14:00:00", 0, "HR-101", "denied")
    al("Frank Foster", "15:30:00", 0, "FIN-101", "granted")
    al("Frank Foster", "08:45:00", 0, "FIN-101", "granted")
    al("Frank Foster", "11:30:00", 0, "FIN-102", "granted")
    al("Frank Foster", "13:00:00", 0, "FIN-201", "denied")
    al("Frank Foster", "16:00:00", 0, "FIN-101", "granted")
    al("Frank Foster", "22:00:00", 0, "FIN-101", "denied")
    al("Frank Foster", "10:00:00", 1, "FIN-101", "denied")
    al("Frank Foster", "09:00:00", 0, "FIN-101", "granted")
    al("Frank Foster", "12:00:00", 0, "FIN-102", "granted")

    # --- 7. Grace Garcia (20 logs) ---
    al("Grace Garcia", "08:30:00", 0, "OPS-202", "granted")
    al("Grace Garcia", "09:45:00", 0, "OPS-101", "granted")
    al("Grace Garcia", "11:00:00", 0, "OPS-201", "granted")
    al("Grace Garcia", "13:00:00", 0, "OPS-202", "granted")
    al("Grace Garcia", "14:30:00", 0, "OPS-301", "granted")
    al("Grace Garcia", "08:00:00", 0, "OPS-202", "granted")
    al("Grace Garcia", "10:00:00", 0, "OPS-102", "granted")
    al("Grace Garcia", "13:30:00", 0, "OPS-201", "granted")
    al("Grace Garcia", "15:00:00", 0, "OPS-202", "granted")
    al("Grace Garcia", "16:30:00", 0, "OPS-101", "granted")
    al("Grace Garcia", "09:00:00", 0, "OPS-202", "granted")
    al("Grace Garcia", "11:30:00", 0, "OPS-301", "granted")
    al("Grace Garcia", "14:00:00", 0, "OPS-201", "granted")
    al("Grace Garcia", "08:30:00", 0, "OPS-202", "granted")
    al("Grace Garcia", "12:00:00", 0, "OPS-102", "granted")
    al("Grace Garcia", "15:30:00", 0, "OPS-202", "granted")
    al("Grace Garcia", "10:00:00", 0, "FIN-101", "denied")
    al("Grace Garcia", "14:00:00", 0, "IT-101", "denied")
    al("Grace Garcia", "23:00:00", 0, "OPS-202", "denied")
    al("Grace Garcia", "09:00:00", 1, "OPS-101", "denied")

    # --- 8. Henry Harris (20 logs) ---
    al("Henry Harris", "09:00:00", 0, "IT-101", "granted")
    al("Henry Harris", "10:30:00", 0, "IT-201", "denied")
    al("Henry Harris", "11:00:00", 0, "IT-102", "denied")
    al("Henry Harris", "14:00:00", 0, "IT-101", "granted")
    al("Henry Harris", "15:30:00", 0, "IT-301", "denied")
    al("Henry Harris", "22:00:00", 0, "IT-101", "denied")
    al("Henry Harris", "23:30:00", 0, "IT-201", "denied")
    al("Henry Harris", "02:00:00", 0, "IT-101", "denied")
    al("Henry Harris", "03:30:00", 0, "FIN-101", "denied")
    al("Henry Harris", "10:00:00", 0, "IT-101", "granted")
    al("Henry Harris", "11:30:00", 0, "HR-101", "denied")
    al("Henry Harris", "13:00:00", 0, "IT-101", "granted")
    al("Henry Harris", "21:00:00", 0, "IT-202", "denied")
    al("Henry Harris", "01:00:00", 0, "OPS-101", "denied")
    al("Henry Harris", "12:00:00", 0, "IT-101", "granted")
    al("Henry Harris", "16:00:00", 0, "IT-101", "granted")
    al("Henry Harris", "20:00:00", 0, "IT-301", "denied")
    al("Henry Harris", "00:30:00", 0, "IT-101", "denied")
    al("Henry Harris", "09:30:00", 0, "IT-101", "granted")
    al("Henry Harris", "17:00:00", 0, "IT-101", "granted")

    # --- 9. Iris Huang (20 logs) ---
    al("Iris Huang", "08:30:00", 0, "FIN-301", "granted")
    al("Iris Huang", "09:45:00", 0, "HR-101", "granted")
    al("Iris Huang", "11:00:00", 0, "OPS-201", "granted")
    al("Iris Huang", "13:00:00", 0, "FIN-301", "granted")
    al("Iris Huang", "14:30:00", 0, "HR-201", "granted")
    al("Iris Huang", "09:00:00", 0, "OPS-101", "granted")
    al("Iris Huang", "10:30:00", 0, "FIN-102", "granted")
    al("Iris Huang", "13:30:00", 0, "HR-102", "granted")
    al("Iris Huang", "15:00:00", 0, "OPS-202", "granted")
    al("Iris Huang", "08:00:00", 0, "FIN-301", "granted")
    al("Iris Huang", "10:00:00", 0, "OPS-301", "granted")
    al("Iris Huang", "11:30:00", 0, "HR-301", "granted")
    al("Iris Huang", "14:00:00", 0, "FIN-201", "granted")
    al("Iris Huang", "16:00:00", 0, "FIN-301", "granted")
    al("Iris Huang", "09:30:00", 0, "HR-201", "granted")
    al("Iris Huang", "11:00:00", 0, "OPS-201", "granted")
    al("Iris Huang", "15:30:00", 0, "IT-101", "denied")
    al("Iris Huang", "22:00:00", 0, "FIN-301", "denied")
    al("Iris Huang", "10:00:00", 1, "FIN-301", "denied")
    al("Iris Huang", "14:00:00", 0, "MKT-101", "denied")

    # --- 10. Jack Johnson (20 logs) ---
    al("Jack Johnson", "09:00:00", 0, "FIN-101", "denied")
    al("Jack Johnson", "10:30:00", 0, "IT-301", "denied")
    al("Jack Johnson", "12:00:00", 0, "HR-201", "denied")
    al("Jack Johnson", "14:00:00", 0, "FIN-201", "denied")
    al("Jack Johnson", "15:30:00", 0, "MKT-101", "denied")
    al("Jack Johnson", "22:00:00", 0, "OPS-101", "denied")
    al("Jack Johnson", "23:00:00", 0, "IT-101", "denied")
    al("Jack Johnson", "01:00:00", 0, "HR-102", "denied")
    al("Jack Johnson", "03:00:00", 0, "FIN-302", "denied")
    al("Jack Johnson", "11:00:00", 0, "OPS-301", "denied")
    al("Jack Johnson", "13:00:00", 0, "MKT-201", "denied")
    al("Jack Johnson", "16:00:00", 0, "IT-202", "denied")
    al("Jack Johnson", "08:00:00", 0, "HR-301", "denied")
    al("Jack Johnson", "20:00:00", 0, "FIN-101", "denied")
    al("Jack Johnson", "02:30:00", 0, "MKT-301", "denied")
    al("Jack Johnson", "10:00:00", 0, "OPS-102", "denied")
    al("Jack Johnson", "14:30:00", 0, "IT-102", "denied")
    al("Jack Johnson", "17:00:00", 0, "HR-101", "denied")
    al("Jack Johnson", "21:00:00", 0, "FIN-201", "denied")
    al("Jack Johnson", "05:00:00", 0, "OPS-202", "denied")

    # --- 11. Karen Kim (20 logs) ---
    al("Karen Kim", "08:00:00", 0, "FIN-101", "granted")
    al("Karen Kim", "09:15:00", 0, "HR-201", "granted")
    al("Karen Kim", "10:30:00", 0, "IT-101", "granted")
    al("Karen Kim", "11:45:00", 0, "MKT-201", "granted")
    al("Karen Kim", "13:00:00", 0, "OPS-202", "granted")
    al("Karen Kim", "08:30:00", 0, "FIN-101", "granted")
    al("Karen Kim", "09:00:00", 0, "FIN-201", "granted")
    al("Karen Kim", "10:00:00", 0, "HR-101", "granted")
    al("Karen Kim", "14:00:00", 0, "IT-201", "granted")
    al("Karen Kim", "15:30:00", 0, "MKT-101", "granted")
    al("Karen Kim", "08:00:00", 0, "FIN-101", "granted")
    al("Karen Kim", "10:00:00", 0, "OPS-101", "granted")
    al("Karen Kim", "11:00:00", 0, "HR-301", "granted")
    al("Karen Kim", "13:30:00", 0, "MKT-301", "granted")
    al("Karen Kim", "15:00:00", 0, "IT-301", "granted")
    al("Karen Kim", "16:30:00", 0, "FIN-101", "granted")
    al("Karen Kim", "09:00:00", 0, "OPS-301", "granted")
    al("Karen Kim", "11:30:00", 0, "FIN-102", "granted")
    al("Karen Kim", "14:30:00", 0, "HR-102", "granted")
    al("Karen Kim", "17:00:00", 0, "FIN-101", "granted")

    # --- 12. Leo Lopez (20 logs) ---
    al("Leo Lopez", "05:30:00", 0, "FIN-101", "granted")
    al("Leo Lopez", "06:15:00", 0, "IT-201", "granted")
    al("Leo Lopez", "06:45:00", 0, "HR-101", "granted")
    al("Leo Lopez", "19:30:00", 0, "MKT-201", "granted")
    al("Leo Lopez", "20:15:00", 0, "OPS-101", "granted")
    al("Leo Lopez", "21:00:00", 0, "FIN-301", "granted")
    al("Leo Lopez", "05:00:00", 0, "OPS-302", "granted")
    al("Leo Lopez", "06:00:00", 0, "HR-201", "granted")
    al("Leo Lopez", "20:00:00", 0, "IT-101", "granted")
    al("Leo Lopez", "21:30:00", 0, "MKT-101", "granted")
    al("Leo Lopez", "05:30:00", 1, "FIN-101", "granted")
    al("Leo Lopez", "06:30:00", 1, "IT-301", "granted")
    al("Leo Lopez", "20:00:00", 1, "OPS-201", "granted")
    al("Leo Lopez", "21:00:00", 1, "HR-102", "granted")
    al("Leo Lopez", "05:45:00", 0, "MKT-301", "granted")
    al("Leo Lopez", "19:00:00", 0, "FIN-102", "granted")
    al("Leo Lopez", "20:30:00", 0, "OPS-202", "granted")
    al("Leo Lopez", "22:00:00", 0, "OPS-302", "granted")
    al("Leo Lopez", "06:00:00", 0, "IT-202", "granted")
    al("Leo Lopez", "21:00:00", 0, "HR-301", "granted")

    # --- 13. Maria Martinez (20 logs) ---
    al("Maria Martinez", "09:00:00", 0, "IT-202", "granted")
    al("Maria Martinez", "10:30:00", 0, "IT-101", "granted")
    al("Maria Martinez", "11:45:00", 0, "IT-201", "granted")
    al("Maria Martinez", "14:00:00", 0, "IT-102", "granted")
    al("Maria Martinez", "15:30:00", 0, "IT-202", "granted")
    al("Maria Martinez", "09:15:00", 0, "IT-202", "granted")
    al("Maria Martinez", "11:00:00", 0, "IT-301", "granted")
    al("Maria Martinez", "13:00:00", 0, "IT-101", "granted")
    al("Maria Martinez", "16:00:00", 0, "IT-201", "granted")
    al("Maria Martinez", "22:00:00", 0, "IT-202", "granted")
    al("Maria Martinez", "23:00:00", 0, "IT-202", "granted")
    al("Maria Martinez", "01:00:00", 0, "IT-101", "granted")
    al("Maria Martinez", "09:00:00", 0, "IT-202", "granted")
    al("Maria Martinez", "14:30:00", 0, "IT-202", "granted")
    al("Maria Martinez", "10:00:00", 1, "IT-202", "granted")
    al("Maria Martinez", "14:00:00", 1, "IT-101", "granted")
    al("Maria Martinez", "10:00:00", 0, "FIN-101", "denied")
    al("Maria Martinez", "15:00:00", 0, "HR-201", "denied")
    al("Maria Martinez", "03:00:00", 0, "MKT-101", "denied")
    al("Maria Martinez", "08:30:00", 0, "IT-202", "granted")

    # --- 14. Nathan Nguyen (20 logs) ---
    al("Nathan Nguyen", "09:00:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "10:00:00", 0, "MKT-102", "granted")
    al("Nathan Nguyen", "11:00:00", 0, "MKT-201", "denied")
    al("Nathan Nguyen", "14:00:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "15:00:00", 0, "MKT-301", "denied")
    al("Nathan Nguyen", "09:30:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "10:30:00", 0, "MKT-102", "granted")
    al("Nathan Nguyen", "11:00:00", 0, "MKT-202", "denied")
    al("Nathan Nguyen", "13:00:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "14:30:00", 0, "FIN-101", "denied")
    al("Nathan Nguyen", "16:00:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "09:00:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "10:00:00", 0, "IT-101", "denied")
    al("Nathan Nguyen", "11:30:00", 0, "MKT-102", "granted")
    al("Nathan Nguyen", "14:00:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "15:00:00", 0, "HR-101", "denied")
    al("Nathan Nguyen", "08:30:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "12:00:00", 0, "MKT-102", "granted")
    al("Nathan Nguyen", "22:00:00", 0, "MKT-101", "denied")
    al("Nathan Nguyen", "10:00:00", 1, "MKT-101", "denied")

    # --- 15. Olivia Owens (20 logs) ---
    al("Olivia Owens", "07:30:00", 0, "FIN-101", "granted")
    al("Olivia Owens", "09:00:00", 0, "HR-201", "granted")
    al("Olivia Owens", "10:00:00", 0, "IT-301", "granted")
    al("Olivia Owens", "11:30:00", 0, "MKT-201", "granted")
    al("Olivia Owens", "13:00:00", 0, "OPS-202", "granted")
    al("Olivia Owens", "14:00:00", 0, "FIN-201", "granted")
    al("Olivia Owens", "15:30:00", 0, "IT-101", "granted")
    al("Olivia Owens", "08:00:00", 0, "FIN-101", "granted")
    al("Olivia Owens", "09:00:00", 1, "FIN-101", "granted")
    al("Olivia Owens", "10:00:00", 1, "OPS-101", "granted")
    al("Olivia Owens", "22:00:00", 0, "FIN-101", "granted")
    al("Olivia Owens", "23:00:00", 0, "IT-202", "granted")
    al("Olivia Owens", "08:30:00", 0, "FIN-101", "granted")
    al("Olivia Owens", "10:00:00", 0, "MKT-301", "granted")
    al("Olivia Owens", "13:30:00", 0, "HR-101", "granted")
    al("Olivia Owens", "15:00:00", 0, "OPS-301", "granted")
    al("Olivia Owens", "09:00:00", 0, "IT-102", "granted")
    al("Olivia Owens", "11:00:00", 0, "FIN-302", "granted")
    al("Olivia Owens", "14:00:00", 0, "MKT-101", "granted")
    al("Olivia Owens", "17:00:00", 0, "FIN-101", "granted")

    # --- 16. Paul Patel (20 logs) ---
    al("Paul Patel", "12:00:00", 0, "IT-102", "granted")
    al("Paul Patel", "13:00:00", 0, "IT-101", "granted")
    al("Paul Patel", "14:30:00", 0, "MKT-201", "granted")
    al("Paul Patel", "15:45:00", 0, "IT-102", "granted")
    al("Paul Patel", "12:30:00", 0, "MKT-101", "granted")
    al("Paul Patel", "14:00:00", 0, "IT-201", "granted")
    al("Paul Patel", "16:00:00", 0, "MKT-102", "granted")
    al("Paul Patel", "12:00:00", 0, "IT-102", "granted")
    al("Paul Patel", "13:30:00", 0, "MKT-301", "granted")
    al("Paul Patel", "15:00:00", 0, "IT-101", "granted")
    al("Paul Patel", "16:30:00", 0, "MKT-201", "granted")
    al("Paul Patel", "12:15:00", 0, "IT-102", "granted")
    al("Paul Patel", "13:00:00", 0, "IT-202", "granted")
    al("Paul Patel", "14:30:00", 0, "MKT-101", "granted")
    al("Paul Patel", "16:00:00", 0, "IT-102", "granted")
    al("Paul Patel", "08:00:00", 0, "IT-102", "denied")
    al("Paul Patel", "10:00:00", 0, "OPS-101", "denied")
    al("Paul Patel", "22:00:00", 0, "IT-102", "denied")
    al("Paul Patel", "12:00:00", 1, "IT-102", "denied")
    al("Paul Patel", "09:00:00", 0, "FIN-101", "denied")

    # --- 17. Quinn Chen (20 logs) ---
    al("Quinn Chen", "09:00:00", 1, "IT-101", "granted")
    al("Quinn Chen", "10:30:00", 1, "IT-201", "granted")
    al("Quinn Chen", "12:00:00", 1, "IT-102", "granted")
    al("Quinn Chen", "14:00:00", 1, "IT-301", "granted")
    al("Quinn Chen", "15:30:00", 1, "IT-101", "granted")
    al("Quinn Chen", "09:00:00", 1, "IT-101", "granted")
    al("Quinn Chen", "11:00:00", 1, "IT-202", "granted")
    al("Quinn Chen", "13:00:00", 1, "IT-101", "granted")
    al("Quinn Chen", "15:00:00", 1, "IT-301", "granted")
    al("Quinn Chen", "08:30:00", 1, "IT-101", "granted")
    al("Quinn Chen", "10:00:00", 1, "IT-102", "granted")
    al("Quinn Chen", "12:30:00", 1, "IT-201", "granted")
    al("Quinn Chen", "14:30:00", 1, "IT-301", "granted")
    al("Quinn Chen", "16:00:00", 1, "IT-101", "granted")
    al("Quinn Chen", "09:00:00", 1, "IT-101", "granted")
    al("Quinn Chen", "10:00:00", 0, "IT-101", "denied")
    al("Quinn Chen", "14:00:00", 0, "IT-101", "denied")
    al("Quinn Chen", "09:00:00", 1, "FIN-101", "granted")
    al("Quinn Chen", "11:00:00", 1, "HR-201", "denied")
    al("Quinn Chen", "22:00:00", 1, "IT-101", "denied")

    # --- 18. Rachel Robinson (20 logs) ---
    al("Rachel Robinson", "22:00:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "23:15:00", 0, "FIN-101", "granted")
    al("Rachel Robinson", "00:30:00", 0, "FIN-301", "granted")
    al("Rachel Robinson", "01:45:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "22:30:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "23:00:00", 0, "FIN-201", "granted")
    al("Rachel Robinson", "00:00:00", 0, "FIN-302", "granted")
    al("Rachel Robinson", "01:00:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "22:00:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "23:30:00", 0, "FIN-101", "granted")
    al("Rachel Robinson", "00:15:00", 0, "FIN-201", "granted")
    al("Rachel Robinson", "01:30:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "22:00:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "23:45:00", 0, "FIN-301", "granted")
    al("Rachel Robinson", "01:00:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "22:30:00", 0, "FIN-102", "granted")
    al("Rachel Robinson", "09:00:00", 0, "FIN-102", "denied")
    al("Rachel Robinson", "22:00:00", 0, "IT-101", "denied")
    al("Rachel Robinson", "23:00:00", 0, "MKT-101", "denied")
    al("Rachel Robinson", "22:00:00", 1, "FIN-102", "denied")

    # --- 19. Sam Stevens (20 logs) ---
    al("Sam Stevens", "02:00:00", 0, "FIN-101", "denied")
    al("Sam Stevens", "02:01:00", 0, "FIN-102", "denied")
    al("Sam Stevens", "02:03:00", 0, "FIN-201", "denied")
    al("Sam Stevens", "02:04:00", 0, "IT-101", "denied")
    al("Sam Stevens", "02:06:00", 0, "HR-101", "denied")
    al("Sam Stevens", "02:07:00", 0, "MKT-101", "denied")
    al("Sam Stevens", "02:09:00", 0, "OPS-101", "denied")
    al("Sam Stevens", "02:10:00", 0, "FIN-301", "denied")
    al("Sam Stevens", "02:12:00", 0, "IT-301", "denied")
    al("Sam Stevens", "02:13:00", 0, "HR-201", "denied")
    al("Sam Stevens", "14:00:00", 0, "FIN-101", "denied")
    al("Sam Stevens", "14:05:00", 0, "IT-101", "denied")
    al("Sam Stevens", "14:10:00", 0, "HR-101", "denied")
    al("Sam Stevens", "14:15:00", 0, "MKT-101", "denied")
    al("Sam Stevens", "03:00:00", 0, "FIN-101", "denied")
    al("Sam Stevens", "03:01:00", 0, "FIN-102", "denied")
    al("Sam Stevens", "03:02:00", 0, "FIN-201", "denied")
    al("Sam Stevens", "03:03:00", 0, "IT-101", "denied")
    al("Sam Stevens", "03:05:00", 0, "HR-101", "denied")
    al("Sam Stevens", "03:06:00", 0, "MKT-101", "denied")

    # --- 20. Tina Turner (20 logs) ---
    al("Tina Turner", "09:00:00", 0, "MKT-301", "granted")
    al("Tina Turner", "10:00:00", 0, "FIN-101", "denied")
    al("Tina Turner", "11:00:00", 0, "MKT-201", "granted")
    al("Tina Turner", "13:00:00", 0, "IT-101", "denied")
    al("Tina Turner", "14:00:00", 0, "MKT-102", "granted")
    al("Tina Turner", "09:30:00", 0, "MKT-301", "granted")
    al("Tina Turner", "10:30:00", 0, "HR-101", "denied")
    al("Tina Turner", "11:30:00", 0, "MKT-101", "granted")
    al("Tina Turner", "14:00:00", 0, "OPS-101", "denied")
    al("Tina Turner", "15:00:00", 0, "MKT-201", "granted")
    al("Tina Turner", "09:00:00", 0, "MKT-301", "granted")
    al("Tina Turner", "10:00:00", 0, "IT-201", "denied")
    al("Tina Turner", "11:00:00", 0, "MKT-301", "granted")
    al("Tina Turner", "14:00:00", 0, "HR-201", "denied")
    al("Tina Turner", "15:30:00", 0, "MKT-102", "granted")
    al("Tina Turner", "08:30:00", 0, "MKT-301", "granted")
    al("Tina Turner", "10:00:00", 0, "FIN-201", "denied")
    al("Tina Turner", "11:00:00", 0, "MKT-301", "granted")
    al("Tina Turner", "22:00:00", 0, "MKT-301", "denied")
    al("Tina Turner", "10:00:00", 1, "MKT-301", "denied")

    # --- Repeated attempts: same person, same room, rapid fire ---
    al("Tina Turner",   "10:00:00", 0, "FIN-101", "denied")
    al("Tina Turner",   "10:01:00", 0, "FIN-101", "denied")
    al("Tina Turner",   "10:03:00", 0, "FIN-101", "denied")
    al("Tina Turner",   "10:04:00", 0, "FIN-101", "denied")
    al("Sam Stevens",   "02:00:00", 0, "FIN-101", "denied")
    al("Sam Stevens",   "02:00:30", 0, "FIN-101", "denied")
    al("Sam Stevens",   "02:01:00", 0, "FIN-101", "denied")
    al("Sam Stevens",   "02:01:30", 0, "FIN-101", "denied")
    al("Sam Stevens",   "02:02:00", 0, "FIN-101", "denied")
    al("Frank Foster",  "09:00:00", 0, "FIN-101", "granted")
    al("Frank Foster",  "09:02:00", 0, "FIN-101", "granted")
    al("Frank Foster",  "09:05:00", 0, "FIN-101", "granted")
    al("Henry Harris",  "22:00:00", 0, "IT-101", "denied")
    al("Henry Harris",  "22:01:00", 0, "IT-101", "denied")
    al("Henry Harris",  "22:03:00", 0, "IT-101", "denied")
    al("Henry Harris",  "22:04:00", 0, "IT-101", "denied")
    al("Henry Harris",  "22:06:00", 0, "IT-101", "denied")
    al("Jack Johnson",  "23:00:00", 0, "FIN-101", "denied")
    al("Jack Johnson",  "23:00:30", 0, "FIN-101", "denied")
    al("Jack Johnson",  "23:01:00", 0, "FIN-101", "denied")
    al("Maria Martinez", "14:00:00", 0, "IT-202", "granted")
    al("Maria Martinez", "14:02:00", 0, "IT-202", "granted")
    al("Maria Martinez", "14:05:00", 0, "IT-202", "granted")
    al("Nathan Nguyen", "09:00:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "09:01:00", 0, "MKT-101", "granted")
    al("Nathan Nguyen", "09:03:00", 0, "MKT-101", "denied")

    # --- Shuffle so logs aren't grouped by user ---
    random.shuffle(logs)

    # --- Insert all logs ---
    for user_id, time_str, is_weekend, location, status in logs:
        room = rooms_by_code.get(location)
        room_id = room.id if room else None
        db.create_access_log(AccessLog(
            user_id=user_id,
            access_time=time_str,
            is_weekend=is_weekend,
            location=location,
            room_id=room_id,
            status=status
        ))

    # --- Summary ---
    cursor = db.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM access_logs")
    logs_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM departments")
    depts_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM rooms")
    rooms_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM user_departments")
    ud_count = cursor.fetchone()[0]

    print(f"[OK] Generated: {depts_count} departments, {rooms_count} rooms, "
          f"{users_count} users, {logs_count} logs, {ud_count} user-dept links")

    print("\n=== SAMPLE ===")
    cursor.execute('''
        SELECT al.id, u.name, al.location, al.status, al.access_time
        FROM access_logs al
        JOIN users u ON al.user_id = u.id
        ORDER BY al.access_time
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"ID:{row[0]:>3} {row[1]:<20} -> {row[2]:<10} [{row[3]:<7}] {row[4]}")

    if not _external_db:
        db.close()


if __name__ == "__main__":
    generate_messy_data("access_control.db")
