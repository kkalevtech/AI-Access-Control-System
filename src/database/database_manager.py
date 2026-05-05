import sqlite3
from src.models import User, AccessLog, Alert


class DatabaseManager:
    def __init__(self, db_path="access_control.db"):
        self.db_path = db_path
        self.connection = None
        self.connect()

    def connect(self):
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def init_db(self):
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                access_level INTEGER NOT NULL DEFAULT 1,
                assigned_room TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                access_time TEXT NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL,
                attempts_count INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        self.connection.commit()

    def create_user(self, user):
        cursor = self.connection.cursor()
        cursor.execute(
            'INSERT INTO users (name, department, access_level, assigned_room) VALUES (?, ?, ?, ?)',
            (user.name, user.department, user.access_level, user.assigned_room)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row['id'],
                name=row['name'],
                department=row['department'],
                access_level=row['access_level'],
                assigned_room=row['assigned_room']
            )
        return None

    def get_all_users(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        return [
            User(
                id=row['id'],
                name=row['name'],
                department=row['department'],
                access_level=row['access_level'],
                assigned_room=row['assigned_room']
            )
            for row in rows
        ]

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
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def create_access_log(self, log):
        cursor = self.connection.cursor()
        cursor.execute(
            'INSERT INTO access_logs (user_id, access_time, location, status, attempts_count) VALUES (?, ?, ?, ?, ?)',
            (log.user_id, log.access_time, log.location, log.status, log.attempts_count)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_access_log(self, log_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM access_logs WHERE id = ?', (log_id,))
        row = cursor.fetchone()
        if row:
            return AccessLog(
                id=row['id'],
                user_id=row['user_id'],
                access_time=row['access_time'],
                location=row['location'],
                status=row['status'],
                attempts_count=row['attempts_count']
            )
        return None

    def get_all_access_logs(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM access_logs')
        rows = cursor.fetchall()
        return [
            AccessLog(
                id=row['id'],
                user_id=row['user_id'],
                access_time=row['access_time'],
                location=row['location'],
                status=row['status'],
                attempts_count=row['attempts_count']
            )
            for row in rows
        ]

    def get_user_access_logs(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM access_logs WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        return [
            AccessLog(
                id=row['id'],
                user_id=row['user_id'],
                access_time=row['access_time'],
                location=row['location'],
                status=row['status'],
                attempts_count=row['attempts_count']
            )
            for row in rows
        ]

    def delete_access_log(self, log_id):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM access_logs WHERE id = ?', (log_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def create_alert(self, alert):
        cursor = self.connection.cursor()
        cursor.execute(
            'INSERT INTO alerts (user_id, alert_type, description, created_at) VALUES (?, ?, ?, ?)',
            (alert.user_id, alert.alert_type, alert.description, alert.created_at)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_alert(self, alert_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM alerts WHERE id = ?', (alert_id,))
        row = cursor.fetchone()
        if row:
            return Alert(
                id=row['id'],
                user_id=row['user_id'],
                alert_type=row['alert_type'],
                description=row['description'],
                created_at=row['created_at']
            )
        return None

    def get_all_alerts(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM alerts')
        rows = cursor.fetchall()
        return [
            Alert(
                id=row['id'],
                user_id=row['user_id'],
                alert_type=row['alert_type'],
                description=row['description'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    def get_user_alerts(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM alerts WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        return [
            Alert(
                id=row['id'],
                user_id=row['user_id'],
                alert_type=row['alert_type'],
                description=row['description'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    def delete_alert(self, alert_id):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
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
            WHERE u.department = ?
        ''', (department,))
        row = cursor.fetchone()
        return {
            'total': row['total'] or 0,
            'granted': row['granted'] or 0,
            'denied': row['denied'] or 0
        }

    def get_access_logs_by_date_range(self, start_date, end_date):
        cursor = self.connection.cursor()
        cursor.execute(
            'SELECT * FROM access_logs WHERE access_time >= ? AND access_time <= ?',
            (start_date, end_date)
        )
        rows = cursor.fetchall()
        return [
            AccessLog(
                id=row['id'],
                user_id=row['user_id'],
                access_time=row['access_time'],
                location=row['location'],
                status=row['status'],
                attempts_count=row['attempts_count']
            )
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

    def get_suspicious_users(self, days=7):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT al.user_id, u.name, COUNT(*) as denied_count
            FROM access_logs al
            JOIN users u ON al.user_id = u.id
            WHERE al.status = 'denied'
            AND datetime(al.access_time) >= datetime('now', ? || ' days')
            GROUP BY al.user_id
            HAVING denied_count >= 3
            ORDER BY denied_count DESC
        ''', (f'-{days}',))
        rows = cursor.fetchall()
        return [
            {'user_id': row['user_id'], 'name': row['name'], 'denied_count': row['denied_count']}
            for row in rows
        ]