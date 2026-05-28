import os
import sqlite3
from src.models import User, AccessLog, Department, Room


DEPT_PREFIX_MAP = {
    'FIN': 'Finance', 'HR': 'HR', 'IT': 'IT',
    'MKT': 'Marketing', 'OPS': 'Operations'
}


class DatabaseManager:
    ALL_ROOMS = ['FIN-101', 'FIN-102', 'FIN-201', 'FIN-202', 'FIN-301', 'FIN-302',
                 'HR-101', 'HR-102', 'HR-201', 'HR-202', 'HR-301', 'HR-302',
                 'IT-101', 'IT-102', 'IT-201', 'IT-202', 'IT-301', 'IT-302',
                 'MKT-101', 'MKT-102', 'MKT-201', 'MKT-202', 'MKT-301', 'MKT-302',
                 'OPS-101', 'OPS-102', 'OPS-201', 'OPS-202', 'OPS-301', 'OPS-302']

    DEPARTMENTS = ['Finance', 'HR', 'IT', 'Marketing', 'Operations']

    def __init__(self, db_path="data/access_control.db"):
        self.db_path = db_path
        self.connection = None
        self.connect()

    def connect(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def init_db(self):
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_code TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT DEFAULT '',
                access_level INTEGER NOT NULL DEFAULT 1,
                assigned_room TEXT,
                assigned_room_id INTEGER,
                FOREIGN KEY (assigned_room_id) REFERENCES rooms(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                department_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
                UNIQUE(user_id, department_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                access_time TEXT NOT NULL,
                is_weekend INTEGER NOT NULL DEFAULT 0,
                location TEXT NOT NULL,
                room_id INTEGER,
                status TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            )
        ''')

        self.connection.commit()

    # --- Departments ---

    def create_department(self, department):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO departments (name) VALUES (?)', (department.name,))
        self.connection.commit()
        return cursor.lastrowid

    def get_all_departments(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM departments ORDER BY name')
        rows = cursor.fetchall()
        return [Department(id=row['id'], name=row['name']) for row in rows]

    def get_department(self, department_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM departments WHERE id = ?', (department_id,))
        row = cursor.fetchone()
        if row:
            return Department(id=row['id'], name=row['name'])
        return None

    def get_department_by_name(self, name):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM departments WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            return Department(id=row['id'], name=row['name'])
        return None

    # --- Rooms ---

    def create_room(self, room):
        cursor = self.connection.cursor()
        cursor.execute(
            'INSERT INTO rooms (room_code, department_id) VALUES (?, ?)',
            (room.room_code, room.department_id)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_all_rooms(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT r.id, r.room_code, r.department_id, d.name as department_name
            FROM rooms r
            JOIN departments d ON r.department_id = d.id
            ORDER BY r.room_code
        ''')
        rows = cursor.fetchall()
        return [
            Room(id=row['id'], room_code=row['room_code'],
                 department_id=row['department_id'], department_name=row['department_name'])
            for row in rows
        ]

    def get_room(self, room_id):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT r.id, r.room_code, r.department_id, d.name as department_name
            FROM rooms r
            JOIN departments d ON r.department_id = d.id
            WHERE r.id = ?
        ''', (room_id,))
        row = cursor.fetchone()
        if row:
            return Room(id=row['id'], room_code=row['room_code'],
                        department_id=row['department_id'], department_name=row['department_name'])
        return None

    def get_room_by_code(self, room_code):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT r.id, r.room_code, r.department_id, d.name as department_name
            FROM rooms r
            JOIN departments d ON r.department_id = d.id
            WHERE r.room_code = ?
        ''', (room_code,))
        row = cursor.fetchone()
        if row:
            return Room(id=row['id'], room_code=row['room_code'],
                        department_id=row['department_id'], department_name=row['department_name'])
        return None

    # --- User Departments (many-to-many) ---

    def set_user_departments(self, user_id, department_ids):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM user_departments WHERE user_id = ?', (user_id,))
        for dept_id in department_ids:
            cursor.execute(
                'INSERT OR IGNORE INTO user_departments (user_id, department_id) VALUES (?, ?)',
                (user_id, dept_id)
            )
        self.connection.commit()

    def get_user_departments(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT d.id, d.name FROM departments d
            JOIN user_departments ud ON d.id = ud.department_id
            WHERE ud.user_id = ?
            ORDER BY d.name
        ''', (user_id,))
        rows = cursor.fetchall()
        return [row['name'] for row in rows]

    def get_user_department_ids(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT department_id FROM user_departments WHERE user_id = ?', (user_id,))
        return [row['department_id'] for row in cursor.fetchall()]

    # --- Users ---

    def create_user(self, user):
        cursor = self.connection.cursor()
        assigned_room_id = user.assigned_room_id
        if assigned_room_id is None and user.assigned_room:
            room = self.get_room_by_code(user.assigned_room)
            if room:
                assigned_room_id = room.id
        cursor.execute(
            'INSERT INTO users (name, role, access_level, assigned_room, assigned_room_id) VALUES (?, ?, ?, ?, ?)',
            (user.name, user.role or '', user.access_level, user.assigned_room, assigned_room_id)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            depts = self.get_user_departments(row['id'])
            return User(
                id=row['id'],
                name=row['name'],
                role=row['role'],
                access_level=row['access_level'],
                assigned_room=row['assigned_room'],
                assigned_room_id=row['assigned_room_id'],
                departments=depts
            )
        return None

    def get_all_users(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users ORDER BY id')
        rows = cursor.fetchall()
        users = []
        for row in rows:
            depts = self.get_user_departments(row['id'])
            users.append(User(
                id=row['id'],
                name=row['name'],
                role=row['role'],
                access_level=row['access_level'],
                assigned_room=row['assigned_room'],
                assigned_room_id=row['assigned_room_id'],
                departments=depts
            ))
        return users

    def update_user(self, user_id, **kwargs):
        fields = ', '.join(f'{key} = ?' for key in kwargs.keys())
        values = list(kwargs.values())
        values.append(user_id)
        cursor = self.connection.cursor()
        cursor.execute(f'UPDATE users SET {fields} WHERE id = ?', values)
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM user_departments WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    # --- Access Logs ---

    def create_access_log(self, log):
        cursor = self.connection.cursor()
        room_id = log.room_id
        if room_id is None and log.location:
            room = self.get_room_by_code(log.location)
            if room:
                room_id = room.id
        cursor.execute(
            'INSERT INTO access_logs (user_id, access_time, is_weekend, location, room_id, status) VALUES (?, ?, ?, ?, ?, ?)',
            (log.user_id, log.access_time, log.is_weekend, log.location, room_id, log.status)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_access_log(self, log_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM access_logs WHERE id = ?', (log_id,))
        row = cursor.fetchone()
        if row:
            return AccessLog(
                id=row['id'], user_id=row['user_id'],
                access_time=row['access_time'], is_weekend=row['is_weekend'],
                location=row['location'], status=row['status'], room_id=row['room_id']
            )
        return None

    def get_all_access_logs(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM access_logs ORDER BY id')
        rows = cursor.fetchall()
        return [
            AccessLog(id=row['id'], user_id=row['user_id'],
                      access_time=row['access_time'], is_weekend=row['is_weekend'],
                      location=row['location'], status=row['status'], room_id=row['room_id'])
            for row in rows
        ]

    def get_user_access_logs(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM access_logs WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        return [
            AccessLog(id=row['id'], user_id=row['user_id'],
                      access_time=row['access_time'], is_weekend=row['is_weekend'],
                      location=row['location'], status=row['status'], room_id=row['room_id'])
            for row in rows
        ]

    def delete_access_log(self, log_id):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM access_logs WHERE id = ?', (log_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.connection.commit()
        return cursor.fetchall()

    def close(self):
        if self.connection:
            self.connection.close()

    def get_all_locations(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT room_code FROM rooms ORDER BY room_code')
            rows = cursor.fetchall()
            if rows:
                return [row['room_code'] for row in rows]
        except Exception:
            pass
        return list(self.ALL_ROOMS)

    # --- Stats helpers ---

    def get_user_access_count(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM access_logs WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return row['count'] if row else 0

    def get_user_access_count_by_status(self, user_id, status):
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM access_logs WHERE user_id = ? AND status = ?', (user_id, status))
        row = cursor.fetchone()
        return row['count'] if row else 0

    def get_location_access_count(self, location):
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM access_logs WHERE location = ?', (location,))
        row = cursor.fetchone()
        return row['count'] if row else 0

    def get_department_access_stats(self, department):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'granted' THEN 1 ELSE 0 END) as granted,
                   SUM(CASE WHEN status = 'denied' THEN 1 ELSE 0 END) as denied
            FROM access_logs al
            JOIN users u ON al.user_id = u.id
            JOIN user_departments ud ON u.id = ud.user_id
            JOIN departments d ON ud.department_id = d.id
            WHERE d.name = ?
        ''', (department,))
        row = cursor.fetchone()
        return {
            'total': row['total'] or 0,
            'granted': row['granted'] or 0,
            'denied': row['denied'] or 0
        }

    def get_access_logs_by_time_range(self, start_time, end_time):
        cursor = self.connection.cursor()
        cursor.execute(
            'SELECT * FROM access_logs WHERE access_time >= ? AND access_time <= ?',
            (start_time, end_time)
        )
        rows = cursor.fetchall()
        return [
            AccessLog(id=row['id'], user_id=row['user_id'],
                      access_time=row['access_time'], is_weekend=row['is_weekend'],
                      location=row['location'], status=row['status'], room_id=row['room_id'])
            for row in rows
        ]

    def get_most_active_users(self, limit=10):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT user_id, COUNT(*) as access_count
            FROM access_logs
            GROUP BY user_id
            ORDER BY access_count DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        return [
            {'user_id': row['user_id'], 'access_count': row['access_count']}
            for row in rows
        ]

    def get_suspicious_users(self, days=None):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT al.user_id, u.name, COUNT(*) as denied_count
            FROM access_logs al
            JOIN users u ON al.user_id = u.id
            WHERE al.status = 'denied'
            GROUP BY al.user_id
            HAVING denied_count >= 3
            ORDER BY denied_count DESC
        ''')
        rows = cursor.fetchall()
        return [
            {'user_id': row['user_id'], 'name': row['name'], 'denied_count': row['denied_count']}
            for row in rows
        ]
