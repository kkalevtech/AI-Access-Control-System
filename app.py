from flask import Flask, render_template, request, jsonify
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
if not analyzer.is_trained:
    try:
        analyzer.train_from_database()
    except:
        pass
access_controller = AccessController(db, dispatcher)
security_manager = SecurityManager(db, dispatcher)

dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)
dispatcher.register_listener("on_multiple_attempts", security_manager.on_multiple_attempts_handler)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    total_users = len(db.get_all_users())
    total_logs = len(db.get_all_access_logs())
    total_alerts = len(db.get_all_alerts())
    recent_alerts = db.get_all_alerts()[-5:] if total_alerts > 0 else []
    return render_template('dashboard.html', 
                       total_users=total_users,
                       total_logs=total_logs,
                       total_alerts=total_alerts,
                       recent_alerts=recent_alerts)


@app.route('/users')
def users():
    all_users = db.get_all_users()
    return render_template('users.html', users=all_users)


@app.route('/access_logs')
def access_logs():
    user_id = request.args.get('user_id')
    if user_id:
        logs = db.get_user_access_logs(int(user_id))
    else:
        logs = db.get_all_access_logs()
    return render_template('access_logs.html', logs=logs)


@app.route('/alerts')
def alerts():
    user_id = request.args.get('user_id')
    if user_id:
        alerts = db.get_user_alerts(int(user_id))
    else:
        alerts = db.get_all_alerts()
    return render_template('alerts.html', alerts=alerts)


@app.route('/request_access', methods=['GET', 'POST'])
def request_access():
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        location = request.form['location']
        result = access_controller.request_access(user_id, location)
        return render_template('access_result.html', result=result)
    users = db.get_all_users()
    return render_template('request_access.html', users=users)


@app.route('/api/users', methods=['GET'])
def api_users():
    users = db.get_all_users()
    return jsonify([u.to_dict() for u in users])


@app.route('/api/access_logs', methods=['GET'])
def api_access_logs():
    logs = db.get_all_access_logs()
    return jsonify([log.to_dict() for log in logs])


@app.route('/api/alerts', methods=['GET'])
def api_alerts():
    alerts = db.get_all_alerts()
    return jsonify([a.to_dict() for a in alerts])


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.json
    user_id = data['user_id']
    location = data['location']
    access_time = data.get('access_time')
    result = analyzer.analyze(user_id, access_time or datetime.now().isoformat(), location)
    return jsonify({'result': result})


if __name__ == '__main__':
    app.run(debug=True)