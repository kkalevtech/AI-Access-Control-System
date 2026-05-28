# Phase 2: Core Classes, Events, and CLI Implementation

**This document provides a step-by-step development plan for implementing the core functionality. Read each section carefully and implement one part at a time.**

---

## Overview

Phase 2 implements the foundational classes and event system required for the access control system. All code in this phase is CLI-only (no GUI).

### Deliverables
- All model classes (User, AccessLog, Alert)
- Event system (EventDispatcher, EventArgs)
- All controller classes (AccessController, SecurityManager)
- File handling class (FileManager)
- Database class (DatabaseManager) - basic structure
- CLI interface for testing
- Unit tests for all classes

---

## Virtual Environment and Dependencies Setup

**Important:** All dependencies must be installed inside a virtual environment (`.venv`) to avoid polluting the global Python installation.

### Step 0.1: Create Virtual Environment

Run these commands from the project root:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Or (Linux/Mac)
source .venv/bin/activate
```

### Step 0.2: Create requirements.txt

**File:** `requirements.txt`

Create the file with these Phase 2 dependencies:

```text
pytest>=7.0.0
pytest-cov>=4.0.0
```

### Step 0.3: Install Dependencies

With virtual environment activated:

```bash
pip install -r requirements.txt
```

### Step 0.4: Verify Installation

```bash
python -m pytest --version
```

You should see pytest version output. If you see an error, the virtual environment is not properly activated.

---

## Part 1: Data Model Classes

**Goal:** Create the data structures that represent users, access logs, and alerts.

### Step 1.1: Create User Class

**File:** `src/models/user.py`

Create a User class with the following attributes:
- `id`: Integer (primary key)
- `name`: String
- `department`: String
- `access_level`: Integer (1-5)
- `assigned_room`: String (can be None)

Implementation requirements:
- Use `__init__` to initialize all attributes
- Add `__repr__` for debugging (e.g., `User(id=1, name="John Smith", ...)`)
- Add a `to_dict()` method that returns a dictionary representation
- Add a `from_dict()` class method to create User from dictionary

### Step 1.2: Create AccessLog Class

**File:** `src/models/access_log.py`

Create an AccessLog class with:
- `id`: Integer (primary key)
- `user_id`: Integer (foreign key reference)
- `access_time`: String (ISO format timestamp)
- `location`: String (room/location accessed)
- `status`: String ("granted" or "denied")
- `attempts_count`: Integer (default 1)

Implementation requirements:
- Use `__init__` to initialize all attributes
- Add `__repr__` for debugging
- Add `to_dict()` method
- Add `from_dict()` class method

### Step 1.3: Create Alert Class

**File:** `src/models/alert.py`

Create an Alert class with:
- `id`: Integer (primary key)
- `user_id`: Integer (foreign key reference)
- `alert_type`: String (type of alert)
- `description`: String (alert details)
- `created_at`: String (ISO format timestamp)

Implementation requirements:
- Use `__init__` to initialize all attributes
- Add `__repr__` for debugging
- Add `to_dict()` method
- Add `from_dict()` class method

### Step 1.4: Create Models Package Init

**File:** `src/models/__init__.py`

Export all model classes:
```python
from .user import User
from .access_log import AccessLog
from .alert import Alert

__all__ = ['User', 'AccessLog', 'Alert']
```

### Step 1.5: Test Model Classes

Create `tests/test_models.py` with tests for:
- User creation and to_dict/from_dict
- AccessLog creation and to_dict/from_dict
- Alert creation and to_dict/from_dict

Run tests to verify:
```bash
python -m pytest tests/test_models.py -v
```

---

## Part 2: Event System

**Goal:** Implement the Observer pattern with event dispatching and custom event arguments.

### Step 2.1: Create Custom Event Argument Classes

**File:** `src/events/event_args.py`

Create three event args classes:

#### AccessEventArgs
- `user_id`: Integer
- `location`: String
- `reason`: String (why access was granted/denied)
- `timestamp`: String

#### AlertEventArgs
- `user_id`: Integer
- `alert_type`: String
- `description`: String
- `created_at`: String

#### SuspiciousBehaviorEventArgs
- `user_id`: Integer
- `score`: Float (suspicion score 0-1)
- `reason`: String (explanation)
- `timestamp`: String

All classes should:
- Use `__init__` to accept parameters
- Have `to_dict()` method for serialization

### Step 2.2: Create EventDispatcher Class

**File:** `src/events/event_dispatcher.py`

The EventDispatcher manages event registration and notification.

Required functionality:
- `register_listener(event_type, callback)`: Add a listener for an event
- `unregister_listener(event_type, callback)`: Remove a listener
- `dispatch_event(event_type, event_args)`: Notify all listeners for an event

Implementation approach:
- Use a dictionary: `{event_type: [list of callbacks]}`
- Event types: "on_suspicious_behavior", "on_access_denied", "on_multiple_attempts"
- Callbacks should receive `event_args` as parameter

### Step 2.3: Create Events Package Init

**File:** `src/events/__init__.py`

Export all event classes:
```python
from .event_args import AccessEventArgs, AlertEventArgs, SuspiciousBehaviorEventArgs
from .event_dispatcher import EventDispatcher

__all__ = ['AccessEventArgs', 'AlertEventArgs', 'SuspiciousBehaviorEventArgs', 'EventDispatcher']
```

### Step 2.4: Test Event System

Create `tests/test_events.py` with tests for:
- Registering and unregistering listeners
- Dispatching events to multiple listeners
- Event args serialization
- Verify each event type has at least 2 listeners working

Run tests:
```bash
python -m pytest tests/test_events.py -v
```

---

## Part 3: Database Manager (Basic Structure)

**Goal:** Create the database manager class with basic SQLite operations.

### Step 3.1: Create DatabaseManager Class

**File:** `src/database/database_manager.py`

Required methods:

#### Initialization
- `__init__(db_path="access_control.db")`: Set database path
- `init_db()`: Create tables if they don't exist

Create tables with this schema:
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    access_level INTEGER NOT NULL DEFAULT 1,
    assigned_room TEXT
);

CREATE TABLE IF NOT EXISTS access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    access_time TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT NOT NULL,
    attempts_count INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### CRUD Operations
- `create_user(user)`: Insert User object, return id
- `get_user(user_id)`: Get user by id, return User or None
- `get_all_users()`: Get all users, return list of User objects
- `update_user(user_id, **kwargs)`: Update user fields
- `delete_user(user_id)`: Delete user by id

- `create_access_log(log)`: Insert AccessLog, return id
- `get_access_log(log_id)`: Get log by id
- `get_all_access_logs()`: Get all logs
- `get_user_access_logs(user_id)`: Get logs for specific user
- `delete_access_log(log_id)`: Delete log

- `create_alert(alert)`: Insert Alert, return id
- `get_alert(alert_id)`: Get alert by id
- `get_all_alerts()`: Get all alerts
- `get_user_alerts(user_id)`: Get alerts for specific user
- `delete_alert(alert_id)`: Delete alert

#### Utility Methods
- `execute_query(query, params=None)`: Execute custom SQL
- `close()`: Close database connection

### Step 3.2: Create Database Package Init

**File:** `src/database/__init__.py`

```python
from .database_manager import DatabaseManager

__all__ = ['DatabaseManager']
```

### Step 3.3: Test Database Manager

Create `tests/test_database.py` with tests for:
- Table creation
- Create/read/update/delete for users
- Create/read/delete for access_logs
- Create/read/delete for alerts
- Execute custom query

Run tests:
```bash
python -m pytest tests/test_database.py -v
```

**Important:** Use a test database file (e.g., `test.db`) for tests to avoid corrupting production data. Clean up test database after tests.

---

## Part 4: File Handling

**Goal:** Create the file manager for JSON, CSV, and log file operations.

### Step 4.1: Create FileManager Class

**File:** `src/files/file_manager.py`

Required methods:

#### Log File Operations
- `write_log(message, log_file="system.log")`: Append message to log file with timestamp
- `read_log(log_file="system.log")`: Read entire log file, return list of lines

#### JSON Operations
- `read_json(file_path)`: Read JSON file, return data (dict or list)
- `write_json(file_path, data)`: Write data to JSON file (pretty printed)
- Handle `FileNotFoundError` and `json.JSONDecodeError`

#### CSV Operations
- `read_csv(file_path)`: Read CSV file, return list of dictionaries
- `write_csv(file_path, data, fieldnames)`: Write list of dicts to CSV
- Handle `FileNotFoundError` and CSV parsing errors

### Step 4.2: Create Files Package Init

**File:** `src/files/__init__.py`

```python
from .file_manager import FileManager

__all__ = ['FileManager']
```

### Step 4.3: Test File Manager

Create `tests/test_file_manager.py` with tests for:
- Writing and reading log files
- Writing and reading JSON files
- Writing and reading CSV files
- Error handling for missing files
- Error handling for invalid JSON/CSV

Run tests:
```bash
python -m pytest tests/test_file_manager.py -v
```

---

## Part 5: Controllers

**Goal:** Create AccessController and SecurityManager for handling access requests and security events.

### Step 5.1: Create AccessController Class

**File:** `src/controllers/access_controller.py`

This class processes access requests and makes allow/deny decisions.

Required attributes:
- `database`: DatabaseManager instance
- `event_dispatcher`: EventDispatcher instance

Required methods:
- `request_access(user_id, location, access_time=None)`: Main method to process access request
  - If access_time is None, use current time
  - Query user from database
  - Check user's access level vs location requirements (optional)
  - Return dict with: granted (bool), reason (str), user_id, location, timestamp

- `grant_access(user_id, location, access_time)`: Log successful access
  - Create AccessLog with status="granted"
  - Return access granted message

- `deny_access(user_id, location, reason, access_time)`: Log denied access
  - Create AccessLog with status="denied"
  - Trigger on_access_denied event
  - Return access denied message

### Step 5.2: Create SecurityManager Class

**File:** `src/controllers/security_manager.py`

This class handles security alerts and monitors suspicious activity.

Required attributes:
- `database`: DatabaseManager instance
- `event_dispatcher`: EventDispatcher instance

Required methods:
- `handle_alert(event_args)`: Process alert events
  - Create Alert in database
  - Log alert details

- `log_denied_access(user_id, location, reason, access_time)`: Log denied access
  - Create Alert with alert_type="access_denied"
  - Store in database

- `monitor_failed_attempts(user_id, time_window_minutes=60)`: Check for multiple failed attempts
  - Query access_logs for user with status="denied" within time window
  - If count > 3, trigger on_multiple_attempts event
  - Return dict with: is_suspicious (bool), attempts_count, time_window

- `on_suspicious_behavior_handler(event_args)`: Event listener for suspicious behavior
  - Handle SuspiciousBehaviorEventArgs
  - Log alert to database
  - Log to file

- `on_access_denied_handler(event_args)`: Event listener for access denied
  - Handle AccessEventArgs
  - Create alert in database

- `on_multiple_attempts_handler(event_args)`: Event listener for multiple attempts
  - Handle AlertEventArgs
  - Create alert in database

### Step 5.3: Create Controllers Package Init

**File:** `src/controllers/__init__.py`

```python
from .access_controller import AccessController
from .security_manager import SecurityManager

__all__ = ['AccessController', 'SecurityManager']
```

### Step 5.4: Test Controllers

Create `tests/test_controllers.py` with tests for:
- AccessController: grant_access, deny_access, request_access
- SecurityManager: handle_alert, log_denied_access, monitor_failed_attempts
- Event listeners integration

Run tests:
```bash
python -m pytest tests/test_controllers.py -v
```

---

## Part 6: CLI Interface

**Goal:** Create a simple command-line interface to test all components.

### Step 6.1: Create CLI Module

**File:** `src/cli.py`

Create a CLI that provides these commands:

```
Commands:
  add_user <name> <department> <access_level> [assigned_room]
  list_users
  add_access_log <user_id> <location> <status>
  list_access_logs [user_id]
  request_access <user_id> <location>
  list_alerts [user_id]
  exit
```

Implementation approach:
- Use input() in a loop for interactive commands
- Parse commands using split()
- Call appropriate DatabaseManager or AccessController methods
- Print results in readable format
- Handle invalid commands gracefully

### Step 6.2: Test CLI

Run the CLI and test all commands:
```bash
python -m src.cli
```

Test scenarios:
1. Add 3 users
2. List users
3. Add access logs for each user
4. List access logs
5. Request access for a user
6. List alerts

---

## Part 7: Integration Testing

**Goal:** Verify all components work together correctly.

### Step 7.1: Create Integration Tests

Create `tests/test_integration.py` that tests:
- Full flow: user added → access requested → logged
- Event dispatching: events trigger correct listeners
- Database persistence: data survives app restart
- File logging: events are logged to file

### Step 7.2: Run All Tests

```bash
python -m pytest tests/ -v
```

Ensure all tests pass before proceeding to Phase 3.

---

## Phase 2 Summary

After completing Phase 2, you should have:

1. **All Model Classes**: User, AccessLog, Alert with full CRUD operations
2. **Event System**: EventDispatcher with custom event args, working Observer pattern
3. **Database**: DatabaseManager with SQLite, all tables, full CRUD
4. **File Handling**: FileManager for JSON, CSV, and log files
5. **Controllers**: AccessController and SecurityManager with event integration
6. **CLI**: Working command-line interface for testing
7. **Tests**: Unit and integration tests for all components

All code should be well-tested and ready for Phase 3 (AI/ML integration, GUI).

---

## Next Steps

Proceed to Phase 3 when Phase 2 is complete and all tests pass.

Phase 3 includes:
- AI/ML model (BehaviorAnalyzer) using sklearn
- Advanced database operations
- Advanced file operations
- GUI implementation (Flask web app)
- Full system integration
- 100% test coverage