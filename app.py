import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from src.database.database_manager import DatabaseManager
from src.controllers.access_controller import AccessController
from src.controllers.security_manager import SecurityManager
from src.ai.analyzer import BehaviorAnalyzer
from src.events.event_dispatcher import EventDispatcher
from datetime import datetime

app = Flask(__name__)

db = DatabaseManager("data/access_control.db")
db.init_db()

needs_seed = True
try:
    c = db.connection.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        needs_seed = False
except Exception:
    pass

if needs_seed:
    print("Generating seed data...")
    from src.seed_data import generate_messy_data
    generate_messy_data("data/access_control.db", db=db)

dispatcher = EventDispatcher()
analyzer = BehaviorAnalyzer(db)

if not analyzer.is_trained:
    print("Training model...")
    analyzer.train_from_database()

access_controller = AccessController(db, dispatcher, analyzer=analyzer)
security_manager = SecurityManager(db, dispatcher)

dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)
dispatcher.register_listener("on_multiple_attempts", security_manager.on_multiple_attempts_handler)


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    users = db.get_all_users()
    logs = db.get_all_access_logs()
    
    total_users = len(users)
    total_logs = len(logs)
    granted = sum(1 for l in logs if l.status == 'granted')
    denied = total_logs - granted
    
    recent = logs[-10:] if logs else []
    
    return render_template('dashboard.html',
                     total_users=total_users,
                     total_logs=total_logs,
                     granted=granted,
                     denied=denied,
                     recent=recent)


@app.route('/users')
def users():
    highlight = request.args.get('highlight', type=int)
    all_users = db.get_all_users()
    return render_template('users.html', users=all_users, highlight=highlight)


@app.route('/access_logs')
def access_logs():
    user_id = request.args.get('user_id', type=int)
    status = request.args.get('status')
    location = request.args.get('location')
    is_weekend = request.args.get('is_weekend', type=int)
    sort_by = request.args.get('sort_by', 'time')
    sort_order = request.args.get('sort_order', 'asc')

    logs = db.get_all_access_logs()
    all_users = db.get_all_users()
    users = {u.id: u.name for u in all_users}

    if user_id:
        logs = [l for l in logs if l.user_id == user_id]
    if status:
        logs = [l for l in logs if l.status == status]
    if location:
        logs = [l for l in logs if location.lower() in l.location.lower()]
    if is_weekend is not None:
        logs = [l for l in logs if l.is_weekend == is_weekend]

    reverse = sort_order == 'desc'
    if sort_by == 'user':
        logs = sorted(logs, key=lambda l: users.get(l.user_id, ''), reverse=reverse)
    elif sort_by == 'time':
        logs = sorted(logs, key=lambda l: l.access_time, reverse=reverse)
    elif sort_by == 'location':
        logs = sorted(logs, key=lambda l: l.location, reverse=reverse)
    elif sort_by == 'status':
        logs = sorted(logs, key=lambda l: l.status, reverse=reverse)
    elif sort_by == 'weekend':
        logs = sorted(logs, key=lambda l: l.is_weekend, reverse=reverse)
    else:
        logs = sorted(logs, key=lambda l: l.id, reverse=reverse)

    all_rooms = db.get_all_rooms()

    return render_template('access_logs.html', logs=logs, users=users,
                           all_users=all_users, all_rooms_data=[{
                               'id': r.id, 'room_code': r.room_code,
                               'department_id': r.department_id,
                               'department_name': r.department_name
                           } for r in all_rooms],
                           user_id=user_id, status=status, location=location,
                           is_weekend=is_weekend, sort_by=sort_by, sort_order=sort_order)


@app.route('/request_access', methods=['GET', 'POST'])
def request_access():
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        location = request.form['location']
        hour = request.form.get('access_hour')
        minute = request.form.get('access_minute')
        second = request.form.get('access_second')
        if hour and minute and second:
            access_time = f'{int(hour):02d}:{int(minute):02d}:{int(second):02d}'
        else:
            access_time = None
        result = access_controller.request_access(user_id, location, access_time)
        user_obj = db.get_user(user_id)
        result['user_name'] = user_obj.name if user_obj else 'Unknown User'
        result['user_role'] = user_obj.role if user_obj else ''
        result['user_assigned_room'] = user_obj.assigned_room if user_obj else ''
        result['user_departments'] = ', '.join(user_obj.departments) if user_obj and user_obj.departments else ''
        return render_template('access_result.html', result=result)
    users = db.get_all_users()
    rooms = db.get_all_rooms()
    users_json = json.dumps([{'id': u.id, 'name': u.name, 'role': u.role, 'room': u.assigned_room} for u in users])
    rooms_json = json.dumps([{'code': r.room_code, 'dept': r.department_name} for r in rooms])
    now_dt = datetime.now()
    now_hour = now_dt.hour
    now_minute = now_dt.minute
    now_second = now_dt.second
    return render_template('request_access.html', users=users, rooms=rooms,
                           users_json=users_json, rooms_json=rooms_json,
                           now_hour=now_hour, now_minute=now_minute, now_second=now_second)


@app.route('/reset-db', methods=['POST'])
def reset_db():
    """Regenerate database and retrain model"""
    cursor = db.connection.cursor()
    cursor.execute("DELETE FROM access_logs")
    cursor.execute("DELETE FROM user_departments")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM rooms")
    cursor.execute("DELETE FROM departments")
    db.connection.commit()
    
    from src.seed_data import generate_messy_data
    generate_messy_data("data/access_control.db", db=db)
    
    result = analyzer.retrain()
    
    return jsonify({'status': 'success', 'result': result})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
