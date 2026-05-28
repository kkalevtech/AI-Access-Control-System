# Phase 3: AI/ML, Database Advanced, GUI, and Full Integration

**This document provides a step-by-step development plan for Phase 3. Read each section carefully, implement one part at a time, and run tests after each step.**

---

## Overview

Phase 3 implements the AI/ML component, advanced features, GUI, and ensures complete test coverage. This builds on the foundation from Phase 2.

### Deliverables
- BehaviorAnalyzer with sklearn ML model
- Advanced database operations with aggregations
- Advanced file operations (import/export)
- Statistical analysis functions
- Flask GUI (web interface)
- Complete test suite with 100% coverage

---

## Virtual Environment and Dependencies Setup

**Important:** All dependencies must be installed inside a virtual environment (`.venv`). If you created one in Phase 2, activate it. If not, create one now.

### Step 0.1: Activate or Create Virtual Environment

If you already have `.venv` from Phase 2, activate it:

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

If `.venv` doesn't exist, create it:

```bash
python -m venv .venv
# Then activate as shown above
```

### Step 0.2: Update requirements.txt

**File:** `requirements.txt`

Update the file with all Phase 3 dependencies:

```text
pytest>=7.0.0
pytest-cov>=4.0.0
flask>=2.0.0
scikit-learn>=1.0.0
pandas>=1.5.0
```

### Step 0.3: Install Dependencies

With virtual environment activated:

```bash
pip install -r requirements.txt
```

### Step 0.4: Verify Installation

```bash
python -m pytest --version
python -c "import flask; import sklearn; import pandas; print('All dependencies installed')"
```

---

## Part 1: AI/ML Component - BehaviorAnalyzer

**Goal:** Implement the ML-based behavior analysis using sklearn DecisionTreeClassifier.

### Step 1.1: Create BehaviorAnalyzer Class

**File:** `src/ai/analyzer.py`

Create a class that analyzes access patterns using machine learning.

#### Required Attributes
- `model`: sklearn DecisionTreeClassifier instance
- `database`: DatabaseManager instance
- `is_trained`: Boolean flag indicating if model is ready

#### Required Methods

##### Feature Extraction
```python
def extract_features(user_id, access_time, location):
    """
    Extract features for a single access attempt.
    Returns dict with:
    - hour: 0-23
    - minute: 0-59
    - day_of_week: 0-6 (Monday=0)
    - is_weekend: 0 or 1
    - access_count_last_hour: number of attempts in last 60 min
    - is_assigned_room: 1 if location == user's assigned_room
    - is_same_department: 1 if location's department matches user's
    - user_access_level: 1-5
    - historical_denied_count: total denied for user
    - is_night_access: 1 if hour between 22-06
    """
```

##### Analysis with Confidence Score
```python
def analyze(user_id, access_time, location):
    """
    Main analysis method.
    1. Extract features using extract_features()
    2. If model not trained, return error
    3. Call model.predict() with features
    4. Call model.predict_proba() to get probability confidence
    5. Return dict with:
       - classification: "Normal" or "Suspicious"
       - confidence_normal: float (0-100%)
       - confidence_suspicious: float (0-100%)
       - reason: explanation of why classification was made
    """
```

```python
def get_prediction_confidence(features):
    """
    Get probability confidence scores.
    Returns dict with:
    - normal_prob: probability of being normal (0-1)
    - suspicious_prob: probability of being suspicious (0-1)
    """
```

##### Frequency Analysis
```python
def get_access_frequency(user_id, time_window_minutes=60):
    """
    Count access attempts for user within time window.
    Returns integer count.
    """
```

```python
def get_historical_denied_count(user_id):
    """
    Count total denied access attempts for user.
    Returns integer count.
    """
```

##### Room/Department Checking
```python
def is_assigned_room(user_id, location):
    """
    Check if location matches user's assigned_room.
    Returns True/False.
    """
```

```python
def is_night_access(hour):
    """
    Check if hour is night time (22:00 - 06:00).
    Returns True/False.
    """
```

##### Model Training
```python
def train_from_database():
    """
    Train the model using data from access_logs table.
    
    Steps:
    1. Query all access_logs with user info (JOIN users)
    2. For each record, extract features
    3. Generate label:
       - Label = 1 (Suspicious) if:
         - is_night_access == 1 OR
         - access_count_last_hour > 3 OR
         - is_assigned_room == 0
       - Label = 0 (Normal) otherwise
    4. Split into X (features) and y (labels)
    5. Train DecisionTreeClassifier
    6. Set self.is_trained = True
    7. Return training results (num_samples, accuracy)
    """
```

##### Model Persistence
```python
def save_model(filepath="model.pkl"):
    """
    Save trained model to file using pickle.
    """
```

```python
def load_model(filepath="model.pkl"):
    """
    Load model from file using pickle.
    Set self.is_trained = True after loading.
    """
```

```python
def retrain():
    """
    Retrain model with current database data.
    Calls train_from_database().
    """
```

### Step 1.2: Create AI Package Init

**File:** `src/ai/__init__.py`

```python
from .analyzer import BehaviorAnalyzer

__all__ = ['BehaviorAnalyzer']
```

### Step 1.3: Test BehaviorAnalyzer

Create `tests/test_analyzer.py` with tests for:
- Feature extraction for various scenarios
- is_night_access() edge cases (hour 22, 23, 0, 1, 5, 6)
- is_assigned_room() matching and non-matching
- get_access_frequency() with different time windows
- get_historical_denied_count()
- train_from_database() with sample data
- save_model() and load_model()
- analyze() with trained and untrained model

Run tests:
```bash
python -m pytest tests/test_analyzer.py -v
```

**Important:** Before testing analyze(), you must have at least 30 access log records in the database. Create seed data first.

---

## Part 2: Integration of AI with Controllers

**Goal:** Connect BehaviorAnalyzer with AccessController and SecurityManager.

### Step 2.1: Update AccessController for AI

**File:** `src/controllers/access_controller.py` (modify existing)

Add BehaviorAnalyzer integration to `request_access()`:

```python
def request_access(self, user_id, location, access_time=None):
    """
    Process access request with AI analysis.
    1. Get current timestamp if not provided
    2. Use BehaviorAnalyzer.analyze() to check behavior
    3. If suspicious:
       - Trigger on_suspicious_behavior event
       - Deny access (or allow with warning based on requirements)
    4. If normal: grant access
    5. Return dict with:
       - granted: bool
       - classification: "Normal" or "Suspicious"
       - confidence_normal: float (0-100%)
       - confidence_suspicious: float (0-100%)
       - reason: explanation string
       - user_id, location, timestamp
    """
```

### Step 2.2: Update SecurityManager for AI Events

**File:** `src/controllers/security_manager.py` (modify existing)

Ensure event handlers properly integrate with AI-triggered events:
- `on_suspicious_behavior_handler()` receives SuspiciousBehaviorEventArgs from BehaviorAnalyzer

### Step 2.3: Create Sample Data Generator

**File:** `src/seed_data.py`

Create a script to generate 20 users and 100+ access log records for testing:

```python
def generate_sample_data():
    """
    Generate sample data for training and testing:
    - 20 users (with different departments and access levels)
    - 100+ access logs (mix of normal and suspicious)
    - Various times (day, night, weekend)
    - Various locations (assigned and non-assigned rooms)
    - Mix of granted and denied status
    - Ensure variety: night access, high frequency, wrong room scenarios
    """
```

Run the seed data generator:
```bash
python -m src.seed_data
```

### Step 2.4: Test AI Integration

Run integration tests:
```bash
python -m pytest tests/ -v
```

Verify that:
- AI analysis runs during access requests
- Suspicious behavior triggers events
- Logs are created correctly

---

## Part 3: Advanced Database Operations

**Goal:** Add aggregation queries, statistics, and advanced filtering.

### Step 3.1: Add Aggregation Methods to DatabaseManager

**File:** `src/database/database_manager.py` (add to existing class)

Add these methods:

```python
def get_user_access_count(user_id):
    """Get total access attempts for a user."""

def get_user_access_count_by_status(user_id, status):
    """Get access attempts filtered by status (granted/denied)."""

def get_location_access_count(location):
    """Get total access attempts for a location."""

def get_department_access_stats(department):
    """Get access stats for a department (total, granted, denied)."""

def get_access_logs_by_date_range(start_date, end_date):
    """Get access logs within date range."""

def get_most_active_users(limit=10):
    """Get users with most access attempts."""

def get_suspicious_users(days=7):
    """Get users with suspicious activity in last N days."""
```

### Step 3.2: Test Advanced Database Operations

Create `tests/test_database_advanced.py` with tests for:
- All aggregation methods
- Date range filtering
- Edge cases (no data, single record, many records)

Run tests:
```bash
python -m pytest tests/test_database_advanced.py -v
```

---

## Part 4: Advanced File Operations

**Goal:** Add import/export functionality and advanced file processing.

### Step 4.1: Add Advanced Methods to FileManager

**File:** `src/files/file_manager.py` (add to existing class)

Add these methods:

```python
def export_users_to_json(filepath, users):
    """Export list of User objects to JSON file."""

def export_access_logs_to_csv(filepath, logs):
    """Export list of AccessLog objects to CSV file."""

def import_users_from_json(filepath):
    """Import users from JSON file, return list of User objects."""

def import_access_logs_from_csv(filepath):
    """Import access logs from CSV file, return list of AccessLog objects."""

def export_alerts_to_json(filepath, alerts):
    """Export alerts to JSON file."""

def backup_database(db_manager, backup_path):
    """Create a backup of the database file."""

def restore_database(db_manager, backup_path):
    """Restore database from backup file."""
```

### Step 4.2: Test Advanced File Operations

Create `tests/test_file_advanced.py` with tests for:
- Export and import of all data types
- Backup and restore functionality
- Error handling for corrupted files

Run tests:
```bash
python -m pytest tests/test_file_advanced.py -v
```

---

## Part 5: Statistical Analysis

**Goal:** Add analysis functions using LINQ-style Python operations.

### Step 5.1: Create Analysis Module

**File:** `src/analysis.py`

Create a module with analysis functions using Python's functional operations:

```python
def analyze_access_patterns(access_logs):
    """
    Analyze access patterns using:
    - filter(): find logs by criteria
    - map(): extract specific fields
    - sorted(): sort by date/location
    - groupby(): group by location/day
    Returns dict with statistics.
    """

def get_peak_access_hours(access_logs):
    """Use reduce() and map() to find peak hours."""

def detect_anomalies(access_logs):
    """
    Use list comprehensions to find anomalous patterns:
    - Very high frequency users
    - Unusual locations
    - Odd time patterns
    """

def generate_access_report(db_manager, start_date, end_date):
    """
    Generate comprehensive report:
    - Total access attempts
    - Success rate
    - Most active users
    - Peak hours
    - Anomalies detected
    """
```

### Step 5.2: Test Analysis Functions

Create `tests/test_analysis.py` with tests for:
- Access pattern analysis
- Peak hours calculation
- Anomaly detection
- Report generation

Run tests:
```bash
python -m pytest tests/test_analysis.py -v
```

---

## Part 6: Flask GUI Implementation

**Goal:** Create the web-based graphical user interface.

### Step 6.1: Create Flask Application

**File:** `app.py`

Create main Flask application:

```python
from flask import Flask, render_template, request, redirect, url_for, jsonify
from src.database.database_manager import DatabaseManager
from src.controllers.access_controller import AccessController
from src.controllers.security_manager import SecurityManager
from src.ai.analyzer import BehaviorAnalyzer
from src.events.event_dispatcher import EventDispatcher
import os

app = Flask(__name__)

# Initialize components
db = DatabaseManager("access_control.db")
dispatcher = EventDispatcher()
analyzer = BehaviorAnalyzer(db)
access_controller = AccessController(db, dispatcher)
security_manager = SecurityManager(db, dispatcher)

# Register event listeners
dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)
dispatcher.register_listener("on_multiple_attempts", security_manager.on_multiple_attempts_handler)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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
    return render_template('request_access.html')

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
```

### Step 6.2: Create HTML Templates

**Directory:** `templates/`

Create these templates:

#### `templates/base.html`
Base template with navigation menu and common layout.

#### `templates/index.html`
Home page with welcome message and quick links.

#### `templates/dashboard.html`
Dashboard showing:
- Total users
- Total access logs
- Recent alerts
- Access statistics chart (optional, use simple HTML/CSS)

#### `templates/users.html`
List of all users with:
- Name, department, access level, assigned room displayed in a table
- Add new user form (with fields: name, department, access_level, assigned_room)
- Edit user: modify existing user details
- Delete user: remove user from system
- Actions column with Edit/Delete buttons for each user

#### `templates/access_logs.html`
Access logs table with:
- User, location, time, status
- Filter by user
- Pagination if needed

#### `templates/alerts.html`
Alerts list with:
- Alert type, description, user, timestamp
- Filter by user

#### `templates/request_access.html`
Form to request access:
- User dropdown: select from existing users (shows name, displays user_id)
- Location input: text field for room/location to access
- Optional: access time override (defaults to current time)
- Submit button labeled "Request Access"
- Optional: "Analyze Only" button to see AI analysis without actually logging

#### `templates/access_result.html`
Show access request result including:
- Granted/Denied status (prominent display)
- Classification result ("Normal" or "Suspicious")
- Confidence percentages: "XX% Normal, XX% Suspicious" (use predict_proba)
- Explanation/reason for the decision
- User and location details
- Timestamp

### Step 6.3: Create CSS Styles

**File:** `static/css/style.css`

Create basic styling for the web interface:
- Navigation bar
- Tables
- Forms
- Cards for dashboard
- Responsive design basics

### Step 6.4: Test Flask App

Run the Flask app:
```bash
python app.py
```

Visit http://127.0.0.1:5000 in browser and test:
1. Home page loads
2. Dashboard shows data
3. Users page lists users
4. Access logs page shows logs
5. Alerts page shows alerts
6. Request access form works
7. API endpoints return JSON

### Step 6.5: Fix Any GUI Issues

Address any bugs or issues discovered during testing.

---

## Part 7: Final Integration and Testing

**Goal:** Ensure all components work together and achieve 100% test coverage.

### Step 7.1: Create Comprehensive Test Suite

**File:** `tests/conftest.py`

Create pytest fixtures:
```python
@pytest.fixture
def test_db():
    """Create test database."""
    # Create in-memory or temp database
    # Add sample data
    # Yield db
    # Cleanup

@pytest.fixture
def event_dispatcher():
    """Create event dispatcher."""
    
@pytest.fixture
def behavior_analyzer(test_db):
    """Create behavior analyzer with test data."""
```

### Step 7.2: Run Coverage Analysis

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

Check coverage report to identify untested code.

### Step 7.3: Add Missing Tests

Add tests for any code not covered:
- Edge cases
- Error handling
- Integration scenarios
- GUI routes (if possible with Flask test client)

### Step 7.4: Final Test Run

```bash
python -m pytest tests/ -v --cov=src
```

Verify:
- All tests pass
- Coverage is 100% (or as close as possible, minimum 90%)

### Step 7.5: System Integration Test

Create `tests/test_full_integration.py` that tests:
1. Full user → access request → AI analysis → event → alert flow
2. Database persistence across restarts
3. File export/import maintains data integrity
4. GUI renders correctly with real data
5. All CRUD operations work end-to-end

Run:
```bash
python -m pytest tests/test_full_integration.py -v
```

---

## Part 8: Documentation and Cleanup

**Goal:** Finalize the project with documentation.

### Step 8.1: Create Requirements File

**File:** `requirements.txt`

List all dependencies:
- flask
- pytest
- pytest-cov
- sklearn (scikit-learn)
- pandas (for analysis)

### Step 8.2: Verify README

Check that `README.md` has:
- Installation instructions
- Usage instructions
- Testing instructions
- Project description

### Step 8.3: Final Verification

Run all tests one more time:
```bash
python -m pytest tests/ -v
```

Ensure:
- All tests pass
- No syntax errors
- No import errors
- Application starts without errors

---

## Phase 3 Summary

After completing Phase 3, you should have:

1. **AI/ML Component**: BehaviorAnalyzer with sklearn, trained from database
2. **Advanced Database**: Aggregation queries, statistics, filtering
3. **Advanced Files**: Import/export, backup/restore
4. **Analysis**: Statistical functions using LINQ-style Python
5. **GUI**: Flask web app with all pages functional
6. **Tests**: Comprehensive test suite with high coverage
7. **Documentation**: Complete README and requirements

### Final Test Coverage Goal
- Minimum 90% code coverage
- All critical paths tested
- All CRUD operations tested
- All event types tested
- All AI methods tested
- GUI routes tested

---

## Important Notes

1. **Database Requirements**: The AI model needs at least 100 access log records to train effectively with good accuracy. The seed data must include 20 users and 100+ access logs with diverse patterns (day/night, granted/denied, assigned/unassigned rooms).

2. **ML Training**: The model trains on ALL existing data in the access_logs table. Use `train_from_database()` to train, and `retrain()` to update after new data is added.

3. **Confidence Scores**: Always use `predict_proba()` to get probability confidence. Display results as "XX% Normal, XX% Suspicious" so users understand how sure the model is.

4. **Testing Order**: Follow the step-by-step order. Don't skip testing after each part.

5. **Error Handling**: Ensure all code has proper try/except blocks and handles errors gracefully.

6. **Clean Code**: Keep code readable and well-organized. No unnecessary comments.

7. **School Project**: The AI model must be explainable for project defense. Decision Tree is perfect for this - you can show the decision path.

---

## Project Complete

When Phase 3 is complete, the AI Access Control System will have:
- Full OOP implementation (6+ classes)
- Event-driven architecture with Observer pattern
- SQLite database with 3 tables and full CRUD
- File handling (JSON, CSV, logs)
- sklearn ML model for behavior analysis
- Flask web GUI
- Comprehensive tests

The system is ready for presentation and defense.