from flask import Flask, render_template, request, jsonify, redirect, url_for
from src.database.database_manager import DatabaseManager
from src.controllers.access_controller import AccessController
from src.controllers.security_manager import SecurityManager
from src.ai.analyzer import BehaviorAnalyzer
from src.events.event_dispatcher import EventDispatcher
from datetime import datetime

app = Flask(__name__)

db = DatabaseManager("access_control.db")
dispatcher = EventDispatcher()
analyzer = BehaviorAnalyzer(db)
access_controller = AccessController(db, dispatcher)
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
    alerts = db.get_all_alerts()
    
    total_users = len(users)
    total_logs = len(logs)
    granted = sum(1 for l in logs if l.status == 'granted')
    denied = total_logs - granted
    
    # Recent activity
    recent = logs[-10:] if logs else []
    
    return render_template('dashboard.html',
                     total_users=total_users,
                     total_logs=total_logs,
                     granted=granted,
                     denied=denied,
                     recent_alerts=len(alerts),
                     recent=recent)


@app.route('/users')
def users():
    all_users = db.get_all_users()
    return render_template('users.html', users=all_users)


@app.route('/access_logs')
def access_logs():
    logs = db.get_all_access_logs()
    users = {u.id: u.name for u in db.get_all_users()}
    return render_template('access_logs.html', logs=logs, users=users)


@app.route('/request_access', methods=['GET', 'POST'])
def request_access():
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        location = request.form['location']
        result = access_controller.request_access(user_id, location)
        return render_template('access_result.html', result=result)
    users = db.get_all_users()
    return render_template('request_access.html', users=users)


@app.route('/reset-db', methods=['POST'])
def reset_db():
    """Regenerate database and retrain model"""
    import os
    db_path = "access_control.db"
    
    # Delete old DB
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Generate new data
    from src.seed_data import generate_messy_data
    generate_messy_data(db_path)
    
    # Reinitialize with new DB
    global db, analyzer, access_controller, security_manager
    db = DatabaseManager(db_path)
    analyzer = BehaviorAnalyzer(db)
    access_controller = AccessController(db, dispatcher)
    security_manager = SecurityManager(db, dispatcher)
    
    result = analyzer.train_from_database()
    
    return jsonify({'status': 'success', 'result': result})


if __name__ == '__main__':
    # Auto-train on startup
    if not analyzer.is_trained:
        print("Auto-training model...")
        analyzer.train_from_database()
    app.run(debug=True, use_reloader=False)