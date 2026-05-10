from datetime import datetime, timedelta
import random
import sqlite3

from src.database.database_manager import DatabaseManager
from src.models import User, AccessLog


ALL_ROOMS = ['IT-101', 'IT-102', 'IT-201', 'IT-202', 'IT-301', 'IT-302',
            'HR-101', 'HR-201', 'HR-301', 
            'FIN-301', 'FIN-302', 'FIN-401', 'FIN-501',
            'MKT-401', 'MKT-402', 'MKT-501',
            'OPS-501', 'OPS-502', 'OPS-601']


def generate_messy_data(db_path="access_control.db"):
    """Generate intentionally messy real-world data"""
    
    # FIXED SEED - same data every time
    random.seed(42)
    
    # Full delete and recreate
    if True:  # Reset
        import os
        if os.path.exists(db_path):
            os.remove(db_path)
    
    db = DatabaseManager(db_path)
    db.init_db()
    
    # FIXED base date - same every run!
    base_date = datetime(2026, 5, 12, 12, 0, 0)

    # Create 30 random users
    names = [
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
        "Ivy", "Jack", "Karen", "Leo", "Maria", "Nathan", "Olivia", "Paul",
        "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xander",
        "Yara", "Zack", "Amy", "Ben", "Carla", "Dan"
    ]
    
    # Map departments to rooms
    dept_rooms = {
        'IT': ['IT-101', 'IT-102', 'IT-201', 'IT-202', 'IT-301', 'IT-302'],
        'HR': ['HR-101', 'HR-201', 'HR-301'],
        'Finance': ['FIN-301', 'FIN-302', 'FIN-401', 'FIN-501'],
        'Marketing': ['MKT-401', 'MKT-402', 'MKT-501'],
        'Operations': ['OPS-501', 'OPS-502', 'OPS-601']
    }
    
    users = []
    for name in names:
        dept = random.choice(['IT', 'HR', 'Finance', 'Marketing', 'Operations'])
        room = random.choice(dept_rooms[dept])
        level = random.randint(1, 5)
        
        user = User(name=name, department=dept, access_level=level, assigned_room=room)
        user.id = db.create_user(user)
        users.append(user)

    # Generate 300 random access logs
    for _ in range(300):
        user = random.choice(users)
        
        # Random location - sometimes own, sometimes not
        if random.random() > 0.4:
            location = user.assigned_room
        else:
            location = random.choice(ALL_ROOMS)
        
        # Random timestamp - spread over 90 days
        days_ago = random.randint(0, 90)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        access_time = base_date - timedelta(days=days_ago, hours=hour, minutes=minute)
        
        # Status: weighted random
        if location == user.assigned_room:
            status = 'granted' if random.random() > 0.1 else 'denied'
        else:
            # Different department - harder to get in
            status = 'granted' if random.random() > 0.6 else 'denied'
        
        db.create_access_log(AccessLog(
            user_id=user.id,
            access_time=access_time.isoformat(),
            location=location,
            status=status
        ))

    # Add SOME intentional patterns (but not all)
    patterns = [
        # Ex-employee (card still works after quit)
        (random.choice(users), 'ex-employee', 5, 'granted'),
        
        # Night shift worker
        (random.choice(users), 'night-shift', 10, 'granted'),
        
        # Always denied
        (random.choice(users), 'denied-always', 8, 'denied'),
        
        # "just this once" turned regular
        (random.choice(users), 'favor-granted', 10, 'granted'),
        
        # Friend helped
        (random.choice(users), 'friend-override', 6, 'granted'),
    ]
    
    for user, pattern_type, count, base_status in patterns:
        for i in range(count):
            days_ago = random.randint(0, 60)
            hour = random.randint(9, 18)
            access_time = base_date - timedelta(days=days_ago, hours=hour)
            
            if pattern_type == 'night-shift':
                hour = random.randint(22, 23) if i%2==0 else random.randint(0, 4)
                access_time = base_date - timedelta(days=days_ago, hours=hour)
            
            location = user.assigned_room
            status = base_status
            
            db.create_access_log(AccessLog(
                user_id=user.id,
                access_time=access_time.isoformat(),
                location=location,
                status=status
            ))

    db.close()
    
    # Summary
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM access_logs")
    logs = cur.fetchone()[0]
    
    # Show random sample
    print(f"[OK] Generated: {users} users, {logs} logs")
    
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