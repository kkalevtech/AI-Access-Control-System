# AI Access Control System — Behavioral Analysis

An intelligent access control system that monitors and analyzes user access attempts using machine learning. The system tracks who enters, when they enter, and where they go, then classifies each attempt as **Normal** or **Suspicious** based on learned behavioral patterns.

Built as a **school project** for 11th Grade AI Programming — all code is educational, explainable, and implements mandatory OOP principles.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Architecture Overview](#architecture-overview)
4. [Classes — Full Reference](#classes--full-reference)
   - [1. User](#1-user)
   - [2. AccessLog](#2-accesslog)
   - [3. Department](#3-department)
   - [4. Room](#4-room)
   - [5. BehaviorAnalyzer](#5-behavioranalyzer)
   - [6. AccessController](#6-accesscontroller)
   - [7. SecurityManager](#7-securitymanager)
   - [8. EventDispatcher](#8-eventdispatcher)
   - [9. FileManager](#9-filemanager)
   - [10. DatabaseManager](#10-databasemanager)
   - [Event Argument Classes](#event-argument-classes)
5. [Database Schema](#database-schema)
6. [Relationships & Object Communication](#relationships--object-communication)
7. [AI/ML Model](#aiml-model)
8. [Event System (Observer Pattern)](#event-system-observer-pattern)
9. [LINQ-Style Data Operations](#linq-style-data-operations)
10. [File Handling](#file-handling)
11. [Exception Handling](#exception-handling)
12. [Project Structure](#project-structure)
13. [Installation](#installation)
14. [Usage](#usage)
15. [Testing](#testing)
16. [Seed Data](#seed-data)

---

## Features

| Feature | Description |
|---------|-------------|
| **AI-Powered Analysis** | Random Forest classifier trained on access logs to detect suspicious patterns |
| **Real-time Monitoring** | Track and evaluate access attempts with instant classification |
| **Event-Driven Architecture** | Observer pattern with 3 event types, each having multiple listeners |
| **Web GUI** | Flask-based interface for managing users, reviewing logs, and requesting access |
| **SQLite Database** | Full CRUD across 5 tables with foreign key relationships |
| **File Operations** | JSON export/import, CSV export/import, log file writing with backup/restore |
| **Statistical Analysis** | LINQ-style data processing using `filter()`, `map()`, `reduce()`, `sorted()`, `groupby()` |

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.x** | Core language |
| **Flask** | Web GUI framework |
| **scikit-learn** | Machine Learning (RandomForestClassifier) |
| **SQLite** | Relational database |
| **pandas** | Data analysis (optional, for extended reporting) |
| **pytest** | Unit and integration testing |

---

## Architecture Overview

The system follows a layered architecture with clear separation of concerns:

```
┌──────────────────────────────────────────────┐
│                  Flask GUI                    │
│         (templates/, static/, app.py)         │
├──────────────────────────────────────────────┤
│                Controllers                    │
│   ┌─────────────────┐ ┌──────────────────┐   │
│   │ AccessController │ │ SecurityManager  │   │
│   └────────┬────────┘ └────────┬─────────┘   │
├────────────┼───────────────────┼──────────────┤
│            ▼                   ▼              │
│   ┌──────────────────────────────────────┐   │
│   │           EventDispatcher            │   │
│   │  (Observer Pattern — 3 event types)  │   │
│   └──────────────────────────────────────┘   │
├────────────┬───────────────────┬──────────────┤
│            ▼                   ▼              │
│   ┌────────────────┐  ┌──────────────────┐   │
│   │ BehaviorAnalyzer │  │ DatabaseManager  │   │
│   │   (AI/ML)       │  │   (SQLite CRUD)  │   │
│   └────────────────┘  └──────────────────┘   │
├──────────────────────────────────────────────┤
│   ┌────────────────┐  ┌──────────────────┐   │
│   │   FileManager  │  │     Models       │   │
│   │ (JSON/CSV/Log) │  │ User/AccessLog/  │   │
│   │                │  │ Dept/Room        │   │
│   └────────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────┘
```

**Object communication flow:**
1. User submits access request via web form
2. `AccessController` receives request, queries `DatabaseManager` for user data
3. `BehaviorAnalyzer` extracts features and runs ML prediction
4. If suspicious, `EventDispatcher` fires events → `SecurityManager` listens and logs
5. Result returned to GUI with confidence scores and reasoning

---

## Classes — Full Reference

The project implements **10 classes** across 6 packages, plus 3 event argument classes.

---

### 1. User

**File:** `src/models/user.py`

Represents a person who accesses the system.

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` / `None` | `None` | Primary key, assigned by database |
| `name` | `str` / `None` | `None` | Full name (e.g. "Alice Anderson") |
| `role` | `str` / `None` | `None` | Job title (e.g. "Finance Director") |
| `access_level` | `int` | `1` | Permission level (1–5, higher = more access) |
| `assigned_room` | `str` / `None` | `None` | Primary room code (e.g. "FIN-201") |
| `assigned_room_id` | `int` / `None` | `None` | Foreign key to rooms table |
| `departments` | `list[str]` | `[]` | Department names this user belongs to |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `__init__(...)` | — | Initializes all attributes |
| `__repr__()` | `str` | Debug representation: `User(id=1, name="Alice Anderson", role="Finance Director", access_level=5, assigned_room="FIN-201")` |
| `to_dict()` | `dict` | Serializes to dictionary (for JSON export) |
| `from_dict(data)` | `User` | Class method — deserializes from dictionary |

---

### 2. AccessLog

**File:** `src/models/access_log.py`

Records a single access attempt.

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` / `None` | `None` | Primary key, assigned by database |
| `user_id` | `int` / `None` | `None` | Foreign key to users table |
| `access_time` | `str` / `None` | `None` | Time in `HH:MM:SS` format |
| `is_weekend` | `int` | `0` | `1` if Saturday/Sunday, `0` otherwise |
| `location` | `str` / `None` | `None` | Room code accessed (e.g. "FIN-201") |
| `status` | `str` | `"granted"` | `"granted"` or `"denied"` |
| `room_id` | `int` / `None` | `None` | Foreign key to rooms table (resolved from location) |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `__init__(...)` | — | Initializes all attributes |
| `__repr__()` | `str` | Debug representation |
| `to_dict()` | `dict` | Serializes to dictionary |
| `from_dict(data)` | `AccessLog` | Class method — deserializes from dictionary |

---

### 3. Department

**File:** `src/models/department.py`

Represents a company department.

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` / `None` | `None` | Primary key |
| `name` | `str` / `None` | `None` | Department name (e.g. "Finance", "IT") |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `__init__(...)` | — | Initializes attributes |
| `__repr__()` | `str` | Debug representation |
| `to_dict()` | `dict` | Serializes to dictionary |
| `from_dict(data)` | `Department` | Class method — deserializes |

**Pre-defined departments:** Finance, HR, IT, Marketing, Operations

---

### 4. Room

**File:** `src/models/room.py`

Represents a physical room/location.

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` / `None` | `None` | Primary key |
| `room_code` | `str` / `None` | `None` | Unique room identifier (e.g. "FIN-101") |
| `department_id` | `int` / `None` | `None` | Foreign key to departments table |
| `department_name` | `str` / `None` | `None` | Resolved department name (joined query) |

#### Room Code Convention

Room codes use the pattern `{DEPT_PREFIX}-{NUMBER}` where:

| Prefix | Department |
|--------|------------|
| FIN | Finance |
| HR | Human Resources |
| IT | Information Technology |
| MKT | Marketing |
| OPS | Operations |

Number suffixes: 101, 102, 201, 202, 301, 302 → **30 rooms total** (5 depts × 6 suffixes)

---

### 5. BehaviorAnalyzer

**File:** `src/ai/analyzer.py`

The AI/ML component that classifies access behavior as Normal or Suspicious using a **Random Forest Classifier** from scikit-learn.

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `database` | `DatabaseManager` | required | Reference to database for feature extraction |
| `model` | `RandomForestClassifier` | `random_state=42, n_estimators=100` | Trained sklearn model |
| `is_trained` | `bool` | `False` | Whether model has been trained |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `extract_features(user_id, access_time, location, is_weekend, reference_time)` | `dict` | Builds feature vector from database queries |
| `analyze(user_id, access_time, location, is_weekend)` | `dict` | Runs prediction, returns classification + confidence + reasons |
| `train_from_database()` | `dict` | Trains model on all access_logs data |
| `retrain()` | `dict` | Alias for `train_from_database()` |
| `save_model(filepath)` | `bool` | Pickles model to disk |
| `load_model(filepath)` | `bool` | Loads pickled model from disk |
| `get_prediction_confidence(features)` | `dict` | Returns probability scores |
| `get_access_frequency(user_id, time_window_minutes, reference_time)` | `int` | Counts attempts in time window |
| `get_historical_denied_count(user_id)` | `int` | Counts all denied attempts for user |
| `is_assigned_room(user_id, location)` | `bool` | Checks if location matches assigned room |
| `is_night_access(hour)` | `bool` | `True` if hour >= 22 or hour < 6 |
| `get_user_location_grant_rate(user_id, location)` | `float` | Ratio of granted to total attempts at location |

#### Feature Vector (9 features)

| # | Feature | Source | Range | Description |
|---|---------|--------|-------|-------------|
| 1 | `hour` | parsed from access_time | 0–23 | Hour of access |
| 2 | `minute` | parsed from access_time | 0–59 | Minute of access |
| 3 | `day_of_week` | computed from is_weekend | 0 or 6 | Weekend flag as day index |
| 4 | `is_weekend` | parameter | 0 or 1 | Saturday/Sunday flag |
| 5 | `access_count_last_hour` | DB query on access_logs | 0+ | Attempts in last 60 minutes |
| 6 | `user_access_level` | users table | 1–5 | User's permission level |
| 7 | `historical_denied_count` | DB query on access_logs | 0+ | Total denied attempts for user |
| 8 | `is_night_access` | computed | 0 or 1 | Access between 22:00–06:00 |
| 9 | `user_location_grant_rate` | DB query on access_logs | 0.0–1.0 | Historical success rate at this location |

#### Labeling (for training)

| Label | Meaning | Criteria |
|-------|---------|----------|
| 0 | Normal | Default (status = "granted") |
| 1 | Suspicious | status = "denied" |

**Note:** Unlike the original design document, labeling uses the actual `status` field from access_logs rather than hard-coded rules. This means the model learns the real patterns present in the seed data.

#### Model Details

- **Algorithm:** `RandomForestClassifier` (not DecisionTree as initially planned)
  - `n_estimators=100` — 100 decision trees in the ensemble
  - `random_state=42` — deterministic training
- **Train/Test Split:** 80/20 with `random_state=42`, stratified
- **Cross-validation:** 5-fold cross-validation reported in training results
- **Training data:** All access_logs with ≥ 30 samples required

#### Reason Generation

The `_generate_reason()` method produces human-readable explanations per feature:

**Normal indicators:**
- "Access during normal hours (XX:00)"
- "Moderate access frequency (X attempts in last hour)"
- "Low access frequency (no recent attempts)"
- "User is accessing their assigned room"
- "Department authorization matches this area"
- "No historical denied attempts"

**Suspicious indicators:**
- "Access during night hours (22:00-06:00)"
- "High access frequency (X attempts in last hour)"
- "Not user's assigned room"
- "No department authorization for this area"
- "User has X historical denied attempts"
- "Low historical grant rate (X%)"
- "No prior access history for this location"

---

### 6. AccessController

**File:** `src/controllers/access_controller.py`

Processes access requests and makes grant/deny decisions, integrating AI analysis.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `database` | `DatabaseManager` | Database for user/log queries |
| `event_dispatcher` | `EventDispatcher` | Event system for dispatching alerts |
| `analyzer` | `BehaviorAnalyzer` | AI analysis engine |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `request_access(user_id, location, access_time)` | `dict` | Main entry point — runs AI analysis, dispatches events, returns decision |
| `grant_access(user_id, location, access_time, is_weekend)` | `dict` | Logs granted access to database |
| `deny_access(user_id, location, reason, access_time, is_weekend)` | `dict` | Logs denied access and dispatches `on_access_denied` event |
| `grant_access_with_analysis(user_id, location, access_time, analysis, is_weekend)` | `dict` | Grants access with AI analysis metadata |

#### Decision Flow

```
request_access()
  ├── User not found? → return {granted: False}
  ├── AI trained?
  │   ├── Yes → analyzer.analyze()
  │   │   ├── Suspicious? → dispatch on_suspicious_behavior + on_access_denied → return {granted: False}
  │   │   └── Normal? → return {granted: True}
  │   └── No → _process_request() (fallback rules)
  └── _process_request() fallback:
      ├── Assigned room match? → grant
      ├── Department match? → grant
      └── Otherwise → deny + dispatch on_access_denied
```

---

### 7. SecurityManager

**File:** `src/controllers/security_manager.py`

Monitors suspicious activity and handles security events. Acts as a listener for all 3 event types.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `database` | `DatabaseManager` | Database for querying logs |
| `event_dispatcher` | `EventDispatcher` | For dispatching `on_multiple_attempts` |
| `file_manager` | `FileManager` | Optional — for writing alert logs |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `monitor_failed_attempts(user_id, time_window_minutes)` | `dict` | Checks for >3 failed attempts in a window; dispatches `on_multiple_attempts` if exceeded |
| `on_suspicious_behavior_handler(event_args)` | `None` | **Listener** — logs suspicious behavior via FileManager |
| `on_access_denied_handler(event_args)` | `None` | **Listener** — logs access denial via FileManager |
| `on_multiple_attempts_handler(event_args)` | `None` | **Listener** — logs multiple attempts via FileManager |

---

### 8. EventDispatcher

**File:** `src/events/event_dispatcher.py`

Implements the **Observer pattern**. Manages event registration and notification.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_listeners` | `dict[str, list[callable]]` | Maps event types to lists of callback functions |

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `register_listener(event_type, callback)` | `None` | Registers a callback for an event type |
| `unregister_listener(event_type, callback)` | `None` | Removes a callback from an event type |
| `dispatch_event(event_type, event_args)` | `None` | Calls all registered callbacks with event_args |
| `get_listeners(event_type)` | `list[callable]` | Returns all listeners for an event type |

#### Registered Event Types

| Event Type | Listeners | Trigger |
|------------|-----------|---------|
| `on_suspicious_behavior` | `SecurityManager.on_suspicious_behavior_handler` | Suspicious AI classification |
| `on_access_denied` | `SecurityManager.on_access_denied_handler` | Denied access request |
| `on_multiple_attempts` | `SecurityManager.on_multiple_attempts_handler` | >3 failed attempts in 60 min |

---

### 9. FileManager

**File:** `src/files/file_manager.py`

Handles all file I/O operations: JSON, CSV, log files, and database backup/restore.

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `write_log(message, log_file)` | `None` | Appends `[timestamp] message` to log file |
| `read_log(log_file)` | `list[str]` | Reads all lines from log file |
| `read_json(file_path)` | `dict` / `list` | Parses JSON file |
| `write_json(file_path, data)` | `None` | Writes pretty-printed JSON |
| `read_csv(file_path)` | `list[dict]` | Parses CSV into list of dicts |
| `write_csv(file_path, data, fieldnames)` | `None` | Writes list of dicts to CSV |
| `export_users_to_json(filepath, users)` | `None` | Exports `list[User]` to JSON |
| `export_access_logs_to_csv(filepath, logs)` | `None` | Exports `list[AccessLog]` to CSV |
| `import_users_from_json(filepath)` | `list[User]` | Imports users from JSON file |
| `import_access_logs_from_csv(filepath)` | `list[AccessLog]` | Imports logs from CSV file |
| `backup_database(db_manager, backup_path)` | `bool` | Copies database file to backup path |
| `restore_database(db_manager, backup_path)` | `bool` | Restores database from backup file |

---

### 10. DatabaseManager

**File:** `src/database/database_manager.py`

Manages all SQLite database operations — schema creation, full CRUD, and aggregation queries.

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_path` | `str` | `"data/access_control.db"` | Path to SQLite database file |
| `connection` | `sqlite3.Connection` | `None` | Active database connection |

#### Schema Management

| Method | Description |
|--------|-------------|
| `__init__(db_path)` | Initializes path and calls `connect()` |
| `connect()` | Opens SQLite connection, enables foreign keys, creates `data/` directory if missing |
| `init_db()` | Creates all 5 tables if they don't exist |

#### CRUD Operations — Users

| Method | Description |
|--------|-------------|
| `create_user(user)` | Insert User → returns `id` |
| `get_user(user_id)` | Get User by id (with departments joined) |
| `get_all_users()` | Get all Users |
| `update_user(user_id, **kwargs)` | Update User fields |
| `delete_user(user_id)` | Delete User + department links |

#### CRUD Operations — Access Logs

| Method | Description |
|--------|-------------|
| `create_access_log(log)` | Insert AccessLog → returns `id` |
| `get_access_log(log_id)` | Get AccessLog by id |
| `get_all_access_logs()` | Get all AccessLogs |
| `get_user_access_logs(user_id)` | Get logs for a specific user |
| `delete_access_log(log_id)` | Delete log by id |

#### CRUD Operations — Departments & Rooms

| Method | Description |
|--------|-------------|
| `create_department(department)` | Insert Department → returns `id` |
| `get_all_departments()` | Get all Departments |
| `get_department(id)` | Get Department by id |
| `get_department_by_name(name)` | Get Department by name |
| `create_room(room)` | Insert Room → returns `id` |
| `get_all_rooms()` | Get all Rooms with department names |
| `get_room(id)` | Get Room by id |
| `get_room_by_code(code)` | Get Room by room_code |

#### User-Department (Many-to-Many)

| Method | Description |
|--------|-------------|
| `set_user_departments(user_id, dept_ids)` | Replace department assignments for a user |
| `get_user_departments(user_id)` | Get department names for a user |
| `get_user_department_ids(user_id)` | Get department IDs for a user |

#### Aggregation / Statistics

| Method | Description |
|--------|-------------|
| `get_user_access_count(user_id)` | Total access attempts for user |
| `get_user_access_count_by_status(user_id, status)` | Attempts filtered by status |
| `get_location_access_count(location)` | Total attempts for a location |
| `get_department_access_stats(department)` | Stats (total, granted, denied) per department |
| `get_access_logs_by_time_range(start, end)` | Logs within time range |
| `get_most_active_users(limit)` | Users with most access attempts |
| `get_suspicious_users(days)` | Users with ≥3 denied attempts |
| `get_all_locations()` | All room codes |
| `execute_query(query, params)` | Execute custom SQL |

---

### Event Argument Classes

**File:** `src/events/event_args.py`

#### AccessEventArgs

| Attribute | Type | Description |
|-----------|------|-------------|
| `user_id` | `int` | User who triggered the event |
| `location` | `str` | Room/location involved |
| `reason` | `str` | Explanation |
| `timestamp` | `str` | When the event occurred |

#### AlertEventArgs

| Attribute | Type | Description |
|-----------|------|-------------|
| `user_id` | `int` | User involved |
| `alert_type` | `str` | Type of alert |
| `description` | `str` | Alert details |
| `created_at` | `str` | When alert was created |

#### SuspiciousBehaviorEventArgs

| Attribute | Type | Description |
|-----------|------|-------------|
| `user_id` | `int` | User with suspicious behavior |
| `score` | `float` | Suspicion confidence (0–100) |
| `reason` | `str` | Explanation of why suspicious |
| `timestamp` | `str` | When behavior was detected |

---

## Database Schema

**File:** `data/access_control.db` (auto-generated on first run)

### Table: `departments`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK AUTOINCREMENT | Unique ID |
| `name` | TEXT | NOT NULL UNIQUE | Department name |

### Table: `rooms`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK AUTOINCREMENT | Unique ID |
| `room_code` | TEXT | NOT NULL | Room identifier (e.g. "FIN-101") |
| `department_id` | INTEGER | NOT NULL, FK → departments(id) | Owning department |

### Table: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK AUTOINCREMENT | Unique user ID |
| `name` | TEXT | NOT NULL | Full name |
| `role` | TEXT | DEFAULT '' | Job title |
| `access_level` | INTEGER | NOT NULL DEFAULT 1 | Permission level (1–5) |
| `assigned_room` | TEXT | nullable | Primary room code |
| `assigned_room_id` | INTEGER | FK → rooms(id) | Room foreign key |

### Table: `user_departments` (junction)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK AUTOINCREMENT | Unique ID |
| `user_id` | INTEGER | NOT NULL, FK → users(id) ON DELETE CASCADE | User reference |
| `department_id` | INTEGER | NOT NULL, FK → departments(id) ON DELETE CASCADE | Department reference |
| | | UNIQUE(user_id, department_id) | Prevents duplicates |

### Table: `access_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK AUTOINCREMENT | Unique log ID |
| `user_id` | INTEGER | NOT NULL, FK → users(id) | User who attempted access |
| `access_time` | TEXT | NOT NULL | Time in `HH:MM:SS` format |
| `is_weekend` | INTEGER | NOT NULL DEFAULT 0 | 1 = weekend, 0 = weekday |
| `location` | TEXT | NOT NULL | Room code accessed |
| `room_id` | INTEGER | FK → rooms(id) | Room foreign key |
| `status` | TEXT | NOT NULL | `"granted"` or `"denied"` |

### Entity-Relationship Diagram

```
departments ──┐
     │        │          users ──── access_logs
     │        │           │
     │        │           │
     └── rooms            │
          │               │
          └─── assigned_room_id
                          
user_departments (junction)
├── user_id → users(id)
└── department_id → departments(id)
```

---

## Relationships & Object Communication

| Objects | How They Communicate | Purpose |
|---------|---------------------|---------|
| `AccessController` → `DatabaseManager` | Method call: `db.get_user()`, `db.create_access_log()` | Fetch users, persist logs |
| `AccessController` → `BehaviorAnalyzer` | Method call: `analyzer.analyze()` | Get AI classification |
| `AccessController` → `EventDispatcher` | Method call: `dispatcher.dispatch_event()` | Fire security events |
| `BehaviorAnalyzer` → `DatabaseManager` | Method call: `db.get_user()`, `db.get_user_access_logs()` | Extract features from DB |
| `SecurityManager` → `EventDispatcher` | Registered as listener: `dispatcher.register_listener()` | Receive events |
| `SecurityManager` → `FileManager` | Method call: `file_manager.write_log()` | Log security events |
| `SecurityManager` → `DatabaseManager` | Method call: `db.get_user_access_logs()` | Monitor failed attempts |
| `EventDispatcher` → listeners | Callback invocation: `callback(event_args)` | Notify all listeners |
| `FileManager` → `DatabaseManager` | Method call: `db_manager.db_path`, `db_manager.close()` | Backup/restore |
| `app.py` → all components | Instantiation + method calls | Wires everything together |

---

## AI/ML Model

### Training Pipeline

```
1. Query all access_logs from database
         │
2. For each log, extract feature vector:
   ┌─────────────────────────────────────┐
   │ hour, minute, is_weekend,           │
   │ access_count_last_hour,             │
   │ user_access_level,                  │
   │ historical_denied_count,            │
   │ is_night_access,                    │
   │ user_location_grant_rate            │
   └─────────────────────────────────────┘
         │
3. Label: 1 if status='denied', else 0
         │
4. Train RandomForestClassifier
   - 100 trees, random_state=42
   - 80/20 train/test split
   - 5-fold cross-validation
         │
5. Model ready for predictions
```

### Prediction Flow (Runtime)

```
New access request (user_id, location, access_time)
         │
1. Extract features (same as training)
         │
2. model.predict([features]) → 0 (Normal) or 1 (Suspicious)
         │
3. model.predict_proba([features]) → confidence %
         │
4. _generate_reason(features) → human-readable explanation
         │
5. Return: {classification, confidence_normal, confidence_suspicious, reason, ...}
```

### Confidence Scores

The model returns two confidence percentages that always sum to ~100%:
- **Confidence Normal** — how sure the model is that behavior is normal
- **Confidence Suspicious** — how sure the model is that behavior is suspicious

These are derived from `predict_proba()`, which returns the probability distribution across both classes. For example, `[0.87, 0.13]` means 87% Normal, 13% Suspicious.

### Model Persistence

- `save_model("model.pkl")` — pickles the trained model to disk
- `load_model("model.pkl")` — loads and restores the model
- `retrain()` — retrains on current database data (for dynamic updates)

### Training Requirements

- Minimum **30 access log records** in the database
- Seed data provides **426 records** with diverse patterns
- Training is automatic on first startup (`app.py`)

---

## Event System (Observer Pattern)

### How It Works

1. **Register:** Listeners subscribe to event types via `register_listener(event_type, callback)`
2. **Dispatch:** When an event occurs, `dispatch_event(event_type, event_args)` calls all registered callbacks
3. **Notify:** Each callback receives the event_args object with relevant data

### Event → Listener Mapping

| Event | Trigger Condition | Primary Listener | Secondary Action |
|-------|-------------------|------------------|------------------|
| `on_suspicious_behavior` | AI classifies as Suspicious | `SecurityManager.on_suspicious_behavior_handler()` | Logs to file |
| `on_access_denied` | AccessController denies request | `SecurityManager.on_access_denied_handler()` | Logs to file |
| `on_multiple_attempts` | >3 failed attempts in 60 min window | `SecurityManager.on_multiple_attempts_handler()` | Logs to file |

### Dispatch Points in Code

| Event | Where Dispatched | Why |
|-------|------------------|-----|
| `on_suspicious_behavior` | `AccessController.request_access()` line 48 | AI classified as Suspicious |
| `on_access_denied` | `AccessController.request_access()` line 54 | AI decision → denied |
| `on_access_denied` | `AccessController._process_request()` line 121 | Fallback rule → denied |
| `on_multiple_attempts` | `SecurityManager.monitor_failed_attempts()` line 48 | >3 failures detected |

### Wiring (in `app.py`)

```python
dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)
dispatcher.register_listener("on_multiple_attempts", security_manager.on_multiple_attempts_handler)
```

Each event has exactly **1 listener** (SecurityManager handler), but the Observer pattern is architecturally ready for additional listeners — you can call `register_listener()` multiple times for the same event.

---

## LINQ-Style Data Operations

**File:** `src/analysis.py`

The `analysis.py` module provides statistical analysis using Python's functional programming tools.

### Functions

| Function | LINQ Equivalent | Python Tools Used | Description |
|----------|----------------|-------------------|-------------|
| `analyze_access_patterns(logs)` | GroupBy, Count | `filter()`, `defaultdict`, list comprehension | Total/granted/denied per location and day type |
| `get_peak_access_hours(logs)` | OrderBy + Take | `map()`, `sorted()`, `defaultdict` | Top 5 hours with most access attempts |
| `detect_anomalies(logs)` | Where, Select | `reduce()`, `map()`, `filter()`, list comprehensions | High-frequency users, unusual locations, odd time patterns |
| `generate_access_report(db, start, end)` | Composite | Calls all 3 above + `get_most_active_users()` | Comprehensive access report |

### LINQ Usage Examples

```python
# filter() — find granted logs
granted = list(filter(lambda log: log.status == 'granted', access_logs))

# map() — extract hour counts to list of dicts
hour_list = list(map(lambda x: {'hour': x[0], 'count': x[1]}, hour_counts.items()))

# reduce() — sum all user access counts
total = reduce(lambda a, b: a + b, map(lambda x: x[1], user_counts.items()), 0)

# sorted() — rank hours by frequency
sorted_hours = sorted(hour_list, key=lambda x: x['count'], reverse=True)

# groupby() — via defaultdict for location grouping
by_location = defaultdict(int)
for log in access_logs:
    by_location[log.location] += 1

# List comprehensions — filter anomalies
high_frequency = [{'user_id': uid, 'count': cnt} for uid, cnt in user_counts.items() if cnt > threshold]
```

---

## File Handling

### Supported Formats

| Format | Read | Write | Import | Export |
|--------|------|-------|--------|--------|
| **JSON** | `read_json()` | `write_json()` | `import_users_from_json()` | `export_users_to_json()` |
| **CSV** | `read_csv()` | `write_csv()` | `import_access_logs_from_csv()` | `export_access_logs_to_csv()` |
| **Log (`.log`)** | `read_log()` | `write_log()` | — | — |

### Database Backup

```python
fm = FileManager()
fm.backup_database(db_manager, "data/backup.db")    # copy DB to backup
fm.restore_database(db_manager, "data/backup.db")   # restore from backup
```

---

## Exception Handling

The project uses `try/except` blocks throughout all layers:

| Layer | Exceptions Caught | Where |
|-------|-------------------|-------|
| **Database** | Various (connection, query errors) | `database_manager.py` — `get_access_logs()`, `execute_query()`, stats methods |
| **AI/ML** | Various (model errors) | `analyzer.py` — `extract_features()`, `get_access_frequency()`, `train_from_database()` |
| **File I/O** | `FileNotFoundError`, `json.JSONDecodeError`, `csv.Error`, `ValueError` | `file_manager.py` — `read_json()`, `read_csv()`, `backup_database()` |
| **Events** | No explicit try/except (event callbacks are wrapped at dispatch) | `event_dispatcher.py` |
| **Controllers** | No explicit try/except (relies on lower layers) | `access_controller.py`, `security_manager.py` |
| **Seed Data** | `PermissionError` | `seed_data.py` — DB file deletion |

### Error Handling Pattern

```python
try:
    # operation that might fail
    result = risky_operation()
    return result
except SpecificException as e:
    # handle gracefully, return fallback
    return default_fallback_value
```

---

## Project Structure

```
AI-Access-Control-System/
├── app.py                        # Flask application entry point
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── AGENTS.md                     # AI agent instructions
├── .gitignore                    # Git ignore rules
├── access_control.db             # (generated at runtime — gitignored)
│
├── data/                         # Runtime data directory
│   ├── .gitkeep                  # Keeps directory tracked in git
│   └── access_control.db         # SQLite database (auto-generated)
│
├── docs/                         # Project documentation
│   ├── project_requirements.md
│   ├── project_topic.md
│   ├── project_implementation_analysis.md
│   ├── data-plan.md
│   ├── phase1/phase1.md
│   ├── phase2/phase2.md
│   └── phase3/phase3.md
│
├── src/                          # Core application source
│   ├── __init__.py               # Package marker
│   │
│   ├── models/                   # Data model classes
│   │   ├── __init__.py
│   │   ├── user.py               # User class
│   │   ├── access_log.py         # AccessLog class
│   │   ├── department.py         # Department class
│   │   └── room.py               # Room class
│   │
│   ├── ai/                       # AI/ML component
│   │   ├── __init__.py
│   │   └── analyzer.py           # BehaviorAnalyzer (RandomForest)
│   │
│   ├── controllers/              # Business logic
│   │   ├── __init__.py
│   │   ├── access_controller.py  # AccessController
│   │   └── security_manager.py   # SecurityManager
│   │
│   ├── events/                   # Observer pattern
│   │   ├── __init__.py
│   │   ├── event_dispatcher.py   # EventDispatcher
│   │   └── event_args.py         # Event argument classes
│   │
│   ├── database/                 # Database layer
│   │   ├── __init__.py
│   │   └── database_manager.py   # DatabaseManager (SQLite CRUD)
│   │
│   ├── files/                    # File I/O
│   │   ├── __init__.py
│   │   └── file_manager.py       # FileManager (JSON/CSV/Log)
│   │
│   ├── analysis.py               # LINQ-style statistical analysis
│   └── seed_data.py              # Sample data generator (426 logs, 20 users)
│
├── templates/                    # Flask HTML templates
│   ├── base.html                 # Base layout + all CSS
│   ├── index.html                # Home page
│   ├── dashboard.html            # Stats dashboard + recent activity
│   ├── users.html                # User list
│   ├── access_logs.html          # Filterable access logs
│   ├── request_access.html       # Access request form with search
│   └── access_result.html        # AI analysis result page
│
├── static/
│   └── css/
│       └── style.css             # Additional styles (if any)
│
└── tests/                        # Test suite
    ├── conftest.py               # Pytest fixtures
    ├── test_models.py            # Model class tests
    ├── test_events.py            # Event system tests
    ├── test_database.py          # Database CRUD tests
    ├── test_database_advanced.py # Aggregation/statistics tests
    ├── test_file_manager.py      # File I/O tests
    ├── test_file_advanced.py     # Import/export/backup tests
    ├── test_analyzer.py          # AI/ML tests
    ├── test_controllers.py       # Controller tests
    ├── test_cli.py               # CLI tests
    ├── test_analysis.py          # LINQ-style analysis tests
    ├── test_integration.py       # Integration tests
    └── test_full_integration.py  # End-to-end system tests
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

```bash
# 1. Clone the repository
git clone <repo-url>
cd AI-Access-Control-System

# 2. Create virtual environment
python -m venv .venv

# 3. Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Dependencies (`requirements.txt`)

```
pytest>=7.0.0
pytest-cov>=4.0.0
flask>=2.0.0
scikit-learn>=1.0.0
pandas>=1.5.0
```

---

## Usage

### Starting the Web GUI

```bash
python app.py
```

On first startup, the system automatically:
1. Creates the `data/` directory (if missing)
2. Creates the SQLite database with all 5 tables
3. Generates seed data (20 users, 5 departments, 30 rooms, 426 access logs)
4. Trains the Random Forest model on the seed data

Then open http://127.0.0.1:5000 in your browser.

### Web Pages

| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Redirects to Dashboard |
| Dashboard | `/dashboard` | Stats cards + recent access activity table |
| Users | `/users` | List all users with roles, departments, access levels |
| Access Logs | `/access_logs` | Filterable log table (by user, status, location, weekend) |
| Request Access | `/request_access` | Form with user/location search + time override |
| Result | (POST to `/request_access`) | AI analysis result with confidence bars + reasons |

### Access Logs Filtering

The `/access_logs` page supports:
- **User filter**: `?user_id=5`
- **Status filter**: `?status=denied`
- **Location search**: `?location=FIN`
- **Weekend filter**: `?is_weekend=1`
- **Sort options**: `?sort_by=time&sort_order=desc` (supports: user, time, location, status, weekend)

---

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run with Coverage

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

Then open `htmlcov/index.html` to view the coverage report.

### Test Files

| File | What It Tests |
|------|---------------|
| `test_models.py` | User, AccessLog, Department, Room creation and serialization |
| `test_events.py` | EventDispatcher registration, dispatch, unregister |
| `test_database.py` | Full CRUD for all tables |
| `test_database_advanced.py` | Aggregation queries, statistics, time ranges |
| `test_file_manager.py` | JSON, CSV, log read/write and error handling |
| `test_file_advanced.py` | Import/export, backup/restore |
| `test_analyzer.py` | Feature extraction, model training, prediction, persistence |
| `test_controllers.py` | AccessController, SecurityManager, event integration |
| `test_cli.py` | CLI interface commands |
| `test_analysis.py` | Pattern analysis, peak hours, anomaly detection |
| `test_integration.py` | Cross-component workflows |
| `test_full_integration.py` | End-to-end system tests |

---

## Seed Data

**File:** `src/seed_data.py`

The system auto-generates **426 access logs** across **20 users** with these characteristics:

| User | Role | Access Level | Profile |
|------|------|-------------|---------|
| Alice Anderson | Finance Director | 5 | Normal user, mostly day access to Finance rooms |
| Bob Brown | IT Security Admin | 5 | Normal + some late IT access |
| Carol Chen | HR Manager | 4 | Normal HR access, weekend denials |
| David Davis | Night Security Guard | 3 | Night worker, accesses many rooms |
| Eve Edwards | Marketing Lead | 4 | Normal + some weekend work |
| Frank Foster | Finance Intern | 1 | Mostly granted, some denied (access level limits) |
| Grace Garcia | Operations Supervisor | 3 | Normal operations + cross-dept denials |
| Henry Harris | Ex-Employee (Deactivated) | 1 | Mostly denied (deactivated), random night access |
| Iris Huang | Cross-Dept Coordinator | 3 | Accesses Finance, HR, Operations |
| Jack Johnson | Suspicious Outsider | 1 | **All attempts denied** — brute force simulation |
| Karen Kim | Executive Assistant | 4 | Cross-department normal access |
| Leo Lopez | Cleaner / Maintenance | 2 | Early morning/late evening access |
| Maria Martinez | Senior Developer | 4 | Normal IT + late night coding sessions |
| Nathan Nguyen | New Marketing Hire | 1 | Mostly granted to own dept, some denials |
| Olivia Owens | CEO | 5 | All-granted cross-department access |
| Paul Patel | Part-Time Consultant | 2 | Afternoon IT/Marketing access |
| Quinn Chen | Weekend IT Support | 3 | Weekend access, weekday denials |
| Rachel Robinson | Night Finance Auditor | 3 | Night Finance access, daytime denials |
| Sam Stevens | Brute Force Simulator | 1 | **Rapid-fire denied attempts** — minute-by-minute |
| Tina Turner | Department Hopper | 2 | Mixed granted/denied across departments |

### Repeated Attempt Patterns (for training)

The seed data includes repeated rapid attempts to simulate brute force and suspicious behavior:
- Tina Turner: 4 rapid denials to FIN-101
- Sam Stevens: 5 rapid denials to FIN-101
- Frank Foster: 3 rapid grants to FIN-101
- Henry Harris: 5 rapid denials to IT-101
- Jack Johnson: 3 rapid denials to FIN-101
- Maria Martinez: 3 rapid grants to IT-202
- Nathan Nguyen: 3 attempts to MKT-101 (2 granted, 1 denied)

All logs are shuffled before insertion so they aren't grouped by user.

### Determinism

The seed data uses `random.seed(42)`, so every generation produces **exactly the same data** — same users, same logs, same shuffle order, same trained model.

---

## Notes

- This is a **school project** — all code is written to be educational and explainable for project defense
- The AI model uses **Random Forest** instead of the simpler Decision Tree originally planned, because the ensemble provides more robust classification while remaining interpretable
- The `data/` directory is created automatically at runtime; the database is generated on first startup
- No alerts table exists in the database — alerts are handled at the event level via `AlertEventArgs` and `SecurityManager`
