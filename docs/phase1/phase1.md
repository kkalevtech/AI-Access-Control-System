# Phase 1: Analysis and Design

## 1. Project Idea (Human Understandable Language)

This project is an AI-powered security system that monitors and analyzes user access attempts to a building or facility. The system tracks who enters, when they enter, and where they go. Using artificial intelligence, it determines whether each access attempt is normal or suspicious based on patterns like:

- Time of access (late night access vs. working hours)
- Frequency of access (too many attempts in a short time)
- Location/room access (unusual departments)

If suspicious behavior is detected, the system alerts security personnel and logs the event. The entire system is built using Object-Oriented Programming in Python with a graphical user interface (web app via Flask), SQLite database, and file handling capabilities.

---

## 2. Classes Description

### Data Model Classes

| Class | Responsibilities | Attributes |
|-------|-----------------|------------|
| **User** | Represents a person who accesses the system | id, name, department, access_level, assigned_room |
| **AccessLog** | Records each access attempt | id, user_id, access_time, location, status (granted/denied), attempts_count |
| **Alert** | Stores security alerts | id, user_id, alert_type, description, created_at |

### AI/ML Logic Class

| Class | Responsibilities | Methods |
|-------|-----------------|---------|
| **BehaviorAnalyzer** | Analyzes access patterns using ML, classifies as normal or suspicious | analyze(), extract_features(), train_from_database(), save_model(), load_model(), retrain() |

### Controller/Manager Class

| Class | Responsibilities | Methods |
|-------|-----------------|---------|
| **AccessController** | Processes access requests, makes allow/deny decisions | request_access(), grant_access(), deny_access() |
| **SecurityManager** | Handles security alerts and monitors suspicious activity | handle_alert(), log_denied_access(), monitor_failed_attempts() |

### Events/Observer Class

| Class | Responsibilities | Methods |
|-------|-----------------|---------|
| **EventDispatcher** | Manages event registration and notification | register_listener(), unregister_listener(), dispatch_event() |

### File Handling Class

| Class | Responsibilities | Methods |
|-------|-----------------|---------|
| **FileManager** | Handles reading/writing JSON, CSV, and log files | write_log(), read_json(), write_json(), read_csv(), write_csv() |

### Database Handling Class

| Class | Responsibilities | Methods |
|-------|-----------------|---------|
| **DatabaseManager** | Manages SQLite database and CRUD operations | init_db(), create(), read(), update(), delete(), execute_query() |

### Custom Event Arguments Classes

| Class | Purpose |
|-------|---------|
| **AccessEventArgs** | Contains data for access-related events |
| **AlertEventArgs** | Contains data for alert events |
| **SuspiciousBehaviorEventArgs** | Contains data when suspicious behavior is detected |

---

## 3. File Structure

```
AI-Access-Control-System/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── docs/
│   ├── project_requirements.md
│   ├── project_topic.md
│   ├── phase1.md           # This document
│   └── phase2.md
├── data/
│   ├── sample_users.json   # Sample user data
│   ├── sample_access.csv   # Sample access logs
│   └── logs/
│       └── system.log     # Application logs
├── database/
│   └── database.py        # Database initialization
├── src/
│   ├── __init__.py
│   ├─�� models/
│   │   ├── __init__.py
│   │   ├── user.py        # User class
│   │   ├── access_log.py  # AccessLog class
│   │   └── alert.py       # Alert class
│   ├── ai/
│   │   ├── __init__.py
│   │   └── analyzer.py    # BehaviorAnalyzer class
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── access_controller.py
│   │   └── security_manager.py
│   ├── events/
│   │   ├── __init__.py
│   │   ├── event_dispatcher.py
│   │   └── event_args.py
│   ├── files/
│   │   ├── __init__.py
│   │   └── file_manager.py
│   └── database/
│       ├── __init__.py
│       └── database_manager.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── access_logs.html
│   ├── users.html
│   └── alerts.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

---

## 4. Database Design

### SQLite Database: `access_control.db`

#### Table 1: users

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user ID |
| name | TEXT | NOT NULL | User's full name |
| department | TEXT | NOT NULL | User's department |
| access_level | INTEGER | NOT NULL DEFAULT 1 | Access level (1-5) |
| assigned_room | TEXT | | Assigned room/cabinet |

#### Table 2: access_logs

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique log ID |
| user_id | INTEGER | FOREIGN KEY REFERENCES users(id) | Reference to user |
| access_time | TEXT | NOT NULL | Timestamp of access |
| location | TEXT | NOT NULL | Room/location accessed |
| status | TEXT | NOT NULL | "granted" or "denied" |
| attempts_count | INTEGER | DEFAULT 1 | Number of attempts |

#### Table 3: alerts

| Column | Type | Constraints | Description |
|--------|------|-------------|--------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique alert ID |
| user_id | INTEGER | FOREIGN KEY REFERENCES users(id) | Reference to user |
| alert_type | TEXT | NOT NULL | Type of alert |
| description | TEXT | | Alert description |
| created_at | TEXT | NOT NULL | Alert creation time |

---

## 5. AI Component Design (Using Machine Learning with sklearn)

### BehaviorAnalyzer Class

The AI component uses a **trained Machine Learning model** (Decision Tree Classifier) from sklearn to classify behavior as Normal or Suspicious.

#### How It Works (True ML Pipeline)

The model is **trained on the access_logs table** from the SQLite database. Each new access attempt becomes a training record.

**Training Data - Features from access_logs + users tables:**
| Feature | Description | Value Range | Source Table |
|---------|-------------|-------------|---------------|
| hour | Hour of access (0-23) | 0-23 | access_logs (extracted) |
| minute | Minute of access (0-59) | 0-59 | access_logs (extracted) |
| day_of_week | Day name (0=Monday) | 0-6 | access_logs (extracted) |
| is_weekend | Is it Saturday/Sunday? | 0 or 1 | computed |
| access_count_last_hour | Attempts in last 60 min | 0+ (unlimited) | access_logs (counted) |
| is_assigned_room | Accessing user's assigned room? | 0 or 1 | users + access_logs |
| is_same_department | Room belongs to user's dept? | 0 or 1 | users + access_logs |
| user_access_level | User's access level | 1-5 | users |
| historical_denied_count | Total denied attempts user | 0+ | access_logs (counted) |
| is_night_access | Access between 22:00-06:00? | 0 or 1 | computed |

**Target (Label):**
| Value | Meaning |
|-------|---------|
| 0 | Normal Behavior |
| 1 | Suspicious Behavior |

**Labeling Rule (for training data):**
- Access is "suspicious" if: night access OR more than 3 attempts/hour OR accessing wrong room
- Otherwise: "normal"

#### Data Flow

```
1. Query Training Data from Database
   SELECT * FROM access_logs JOIN users ON access_logs.user_id = users.id

2. Feature Extraction (per record)
   - Parse access_time to hour, minute, day_of_week
   - Count attempts in last hour for same user
   - Check if location == assigned_room
   - Check department match
   - Count historical denials

3. Label Creation
   - If hour >= 22 OR hour < 6 → suspicious (label=1)
   - If access_count_last_hour > 3 → suspicious (label=1)
   - If NOT is_assigned_room → suspicious (label=1)
   - Else → normal (label=0)

4. Train Model
   - X = features (all columns except label)
   - y = label
   - clf = DecisionTreeClassifier()
   - clf.fit(X, y)

5. Save and Use
   - pickle.dump(clf, open('model.pkl', 'wb'))
   - For predictions on new data
```

#### AI Methods

| Method | Purpose |
|--------|---------|
| analyze(user_id, access_time, location) | Main analysis - extracts features and predicts |
| extract_features(user_id, access_time, location) | Query DB and build feature vector |
| get_access_frequency(user_id, time_window) | Count attempts in time window (unlimited) |
| get_historical_denied_count(user_id) | Count all denied attempts for user |
| is_assigned_room(user_id, location) | Check if location matches assigned room |
| is_night_access(hour) | Check if hour is night (22:00-06:00) |
| train_from_database() | Train model using current access_logs data |
| save_model(path) | Save trained model to file |
| load_model(path) | Load model from file |
| retrain() | Retrain with updated data |

#### Real Database Query Example

```sql
-- Get features for training
SELECT 
    CAST(strftime('%H', access_time) AS INTEGER) as hour,
    CAST(strftime('%M', access_time) AS INTEGER) as minute,
    CAST(strftime('%w', access_time) AS INTEGER) as day_of_week,
    CASE WHEN CAST(strftime('%w', access_time) IN ('0', '6') THEN 1 ELSE 0 END as is_weekend,
    u.assigned_room,
    u.department,
    u.access_level,
    l.location
FROM access_logs l
JOIN users u ON l.user_id = u.id
```

#### Training Data Generation

The system will automatically generate training data from the access_logs table. For each record:
- Extract time features from access_time
- Query database for frequency counts
- Apply labeling rules to create labels
- This creates dynamic, real data training

#### Decision Flow (Runtime)

1. AccessController receives access request (user_id, access_time, location)
2. BehaviorAnalyzer.extract_features() queries database
3. Builds feature vector: [hour, minute, day_of_week, is_weekend, access_count_last_hour, is_assigned_room, is_same_department, user_access_level, historical_denied_count, is_night_access]
4. Loads trained model
5. Calls model.predict([features])
6. Returns "Normal" or "Suspicious"
7. AccessController decides: grant or deny
8. Event dispatcher notifies listeners

#### Why Decision Tree?

- **Interpretable**: Can explain the decision path
- **Fast**: No complex computation
- **Works with mixed data**: Handles numerical + categorical
- **Suitable for school project**: Easy to understand and explain
- **Dynamic training**: Can retrain from database anytime

---

## 6. Example Data

### Sample Users (JSON)

```json
[
  {
    "id": 1,
    "name": "John Smith",
    "department": "IT",
    "access_level": 3,
    "assigned_room": "Room 101"
  },
  {
    "id": 2,
    "name": "Sarah Johnson",
    "department": "HR",
    "access_level": 2,
    "assigned_room": "Room 205"
  },
  {
    "id": 3,
    "name": "Mike Davis",
    "department": "Finance",
    "access_level": 3,
    "assigned_room": "Room 302"
  }
]
```

### Training Data

The model trains from the **access_logs table** in the database. Labels are automatically generated using rules:

**Labeling Rules (for training data):**
- **Suspicious (label=1)**: is_night_access OR access_count_last_hour > 3 OR NOT is_assigned_room
- **Normal (label=0)**: Otherwise

**Example Training Data (auto-generated from access_logs):**

| hour | minute | day_of_week | is_weekend | access_count_last_hour | is_assigned_room | is_same_department | user_access_level | historical_denied | is_night | label |
|------|--------|-------------|------------|-----------------------|-------------------|------------------|-------------------|------------------|-------------------|
| 9 | 30 | 0 | 0 | 1 | 1 | 1 | 3 | 0 | 0 | 0 |
| 14 | 15 | 0 | 0 | 1 | 1 | 1 | 2 | 0 | 0 | 0 |
| 23 | 45 | 0 | 0 | 1 | 1 | 1 | 3 | 0 | 1 | 1 |
| 10 | 0 | 5 | 0 | 5 | 1 | 1 | 2 | 0 | 0 | 1 |
| 3 | 20 | 6 | 1 | 3 | 0 | 0 | 1 | 2 | 1 | 1 |

**Note**: The system needs at least 30 records in access_logs to train. New users should generate multiple access attempts over time.

### ML Model Prediction Examples (ML Predictions)

| access_time | location | Access freq (last hour) | Assigned room | User dept | Is Night? | ML Prediction |
|------------|----------|---------------------|---------------|----------|-----------|--------------|
| Monday 09:30 | Room 101 | 1 | Room 101 | IT | No | Normal |
| Monday 23:30 | Room 101 | 1 | Room 101 | IT | Yes (23:30) | Suspicious |
| Saturday 10:00 | Room 205 | 1 | Room 205 | HR | No | Normal |
| Friday 02:00 | Room 302 | 3 | Room 302 | Finance | Yes (02:00) | Suspicious |
| Tuesday 14:00 | Room 101 | 5 | Room 101 | HR | No | Suspicious |

When a new access attempt comes in:
1. System queries access_logs for frequency count
2. Queries users table for assigned_room and department
3. Extracts time features (hour, minute, day_of_week)
4. Builds feature vector
5. Model predicts: "Normal" or "Suspicious"

---

## 7. Events Design

### Event: on_suspicious_behavior

- **Trigger**: When BehaviorAnalyzer returns "Suspicious"
- **Listeners**: SecurityManager, FileLogger
- **EventArgs**: SuspiciousBehaviorEventArgs (user_id, score, reason)

### Event: on_access_denied

- **Trigger**: When access is denied
- **Listeners**: SecurityManager, AlertSystem
- **EventArgs**: AccessEventArgs (user_id, location, reason)

### Event: on_multiple_attempts

- **Trigger**: More than 3 attempts in 1 hour
- **Listeners**: SecurityManager, DatabaseManager
- **EventArgs**: AlertEventArgs (user_id, attempts_count, time_window)

---

## 8. LINQ-Style Operations

The system uses Python's functional programming tools:

| Operation | Use Case |
|-----------|----------|
| `filter()` | Find access logs by date range |
| `map()` | Extract user names from logs |
| `reduce()` | Calculate total access attempts |
| `sorted()` | Sort users by access count |
| `groupby()` | Group logs by location |
| List comprehension | Find suspicious behavior patterns |

---

## 9. Exception Handling

| Exception | Purpose |
|-----------|---------|
| `DatabaseError` | Database connection/query errors |
| `FileOperationError` | File reading/writing errors |
| `AIAnalysisError` | AI model errors |
| `ValidationError` | Input validation errors |

---

## Summary

This Phase 1 document defines:

- The complete project idea in plain language
- 6+ classes covering all OOP requirements
- File structure for a Flask web application
- Database schema with 3 tables
- Previously rule-based AI classification (old)
+ Machine Learning using sklearn - trains from access_logs table in database
- Example data for testing
- Event-driven architecture
- LINQ-style data operations