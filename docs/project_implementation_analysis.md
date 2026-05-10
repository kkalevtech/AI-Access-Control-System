# AI Access Control System - Technical Implementation Analysis

## Document Overview

This document provides comprehensive technical analysis of the AI Access Control System project, covering architecture, implementation details, AI/ML components, database design, event systems, and inter-object communication patterns. The documentation is designed to help developers understand the system fully, prepare for project defense, and support future maintenance.

---

# 1. Project Overview

## 1.1 System Purpose and Core Functionality

The AI Access Control System is a security application that monitors and controls user access to physical spaces within an organization. The system integrates artificial intelligence to analyze access patterns in real-time and detect suspicious behavior before granting or denying access requests. This represents a modern approach to physical security that combines traditional access control mechanisms with machine learning for intelligent threat detection.

The system serves multiple stakeholders: security personnel who need monitoring capabilities, IT administrators who manage user credentials and permissions, and the organization at large whose physical assets require protection. By automating threat detection through AI, the system reduces the burden on human security staff while improving response times to potential security incidents.

The core value proposition lies in its ability to learn from historical access patterns and identify anomalies that would be difficult or time-consuming for human monitors to detect. For example, a user who typically accesses only IT areas attempting to enter HR departments at 3 AM would trigger the AI model to classify this as suspicious behavior, even though such access might appear legitimate on the surface.

## 1.2 Security and Access Control Scenario

The system models a corporate or institutional access control scenario where users belong to different departments and have varying levels of access to physical locations. Each user is assigned an access level (1-5) and an assigned room or cabinet. Users should normally access only their assigned areas or areas within their department prefix.

The threat model addresses several attack vectors: unauthorized access attempts by external parties, legitimate users attempting to access restricted areas, unusual access patterns that may indicate compromised credentials, and brute force attempts through repeated access requests. The AI component specifically focuses on behavioral analysis rather than simply enforcing static rules, allowing it to detect novel attack patterns that Rule-based systems might miss.

The system maintains a complete audit trail of all access attempts, both successful and denied, enabling security administrators to investigate incidents after the fact and identify patterns of suspicious activity over time. This forensic capability is essential for post-incident analysis and continuous improvement of security policies.

## 1.3 AI Behavior Analysis Concept

The AI component uses classification to determine whether an access attempt exhibits normal or suspicious characteristics. This is fundamentally a binary classification problem where the model outputs either "Normal" or "Suspicious" along with confidence scores for each classification.

The model analyzes access behavior across three primary dimensions. Time-based analysis examines when access attempts occur, with particular attention to unusual hours such as nighttime (22:00-06:00) or weekends. Frequency analysis tracks how often a user attempts access within short time windows, as high-frequency attempts may indicate credential sharing or brute force attacks. Location analysis considers whether the requested location matches the user's assigned room or department, with access to non-assigned areas receiving scrutiny.

This multi-faceted approach allows the system to combine multiple weak signals into a stronger overall assessment. For instance, accessing a non-assigned room during normal hours might be flagged but not immediately denied, while the same access attempt at night would almost certainly be denied as suspicious.

## 1.4 Architecture Overview

The system follows a modular, event-driven architecture that separates concerns across distinct components. The architecture can be visualized as a layered system where each layer depends on the layers below it:

| Layer | Components | Responsibility |
|-------|------------|----------------|
| Presentation | Flask templates, Web GUI | User interface and data visualization |
| Application | AccessController, SecurityManager | Business logic and access decision making |
| Analysis | BehaviorAnalyzer, analysis.py | AI/ML processing and statistical analysis |
| Infrastructure | DatabaseManager, FileManager | Data persistence and file operations |
| Events | EventDispatcher | Inter-component communication |

The Flask web server handles HTTP requests and renders templates for the web interface. When an access request is submitted, the controller processes the request by invoking the AI analyzer. The analyzer returns a classification, and based on this classification, the controller either grants or denies access. Both the classification decision and any security events (suspicious behavior, denied access) are dispatched to registered listeners through the event system. The database persists all data, while the file manager handles exports, imports, and logging.

---

# 2. Folder Structure Analysis

## 2.1 Root Directory Organization

```
AI-Access-Control-System/
├── app.py                      # Flask application entry point
├── src/                       # Core source code
│   ├── ai/                    # AI/ML components
│   ├── analysis.py             # Statistical analysis functions
│   ├── cli.py                  # Command-line interface
│   ├── controllers/            # Business logic controllers
│   ├── database/              # Database management
│   ├── events/                # Event system
│   ├── files/                 # File operations
│   ├── models/                # Data models
│   ├── seed_data.py           # Sample data generation
│   └── __init__.py
├── templates/                  # Flask HTML templates
├── static/css/                # Stylesheets
├── tests/                     # Test suite
├── docs/                      # Documentation
└── README.md                  # Project overview
```

The root directory contains the application entry point (`app.py` for the Flask web application) as the primary executable. The `src/` directory houses all modular application code, organized by functional responsibility. This separation ensures maintainability: adding new features or modifying existing behavior requires changes only within the relevant module.

## 2.2 Source Code Modules

### src/ai/ - AI/ML Components

**Purpose:** Contains the machine learning components that power the behavior analysis system.

**Files:**
- `analyzer.py` - The BehaviorAnalyzer class implementing classification logic

**Key Responsibilities:**
- Feature extraction from raw access data
- Model training from historical access logs
- Prediction and classification
- Confidence scoring

**External Dependencies:**
- scikit-learn (DecisionTreeClassifier)
- Python pickle for model serialization
- datetime for temporal feature extraction

### src/controllers/ - Business Logic

**Purpose:** Contains the controllers that implement the core business logic of access control.

**Files:**
- `access_controller.py` - Processes access requests and coordinates with AI
- `security_manager.py` - Handles security events and alerts

**Key Responsibilities:**
- AccessController processes individual access requests, integrates with the AI analyzer, and determines whether to grant or deny access based on AI analysis or fallback rules.
- SecurityManager listens for security events from the event dispatcher, creates alerts in the database, and monitors for repeated failed access attempts.

**Interaction:** These controllers form the core business logic layer. AccessController depends on BehaviorAnalyzer for AI-powered decisions and on the EventDispatcher for triggering events. SecurityManager depends on both the database (for alert storage) and the event system (for receiving security-related events).

### src/database/ - Database Management

**Purpose:** Handles all SQLite database operations including connection management, schema creation, and CRUD operations.

**Files:**
- `database_manager.py` - Complete database abstraction layer

**Key Responsibilities:**
- SQLite connection management with thread-safe configuration
- Schema creation for users, access_logs, and alerts tables
- Full CRUD operations for all entities
- Advanced query methods for analytics and reporting
- Transaction handling

**Database Schema:**
The system uses three primary tables (detailed in Section 6):
- `users` - System users with credentials and access rights
- `access_logs` - Complete audit trail of access attempts
- `alerts` - Security alerts and notifications

### src/events/ - Event System

**Purpose:** Implements the observer pattern for loose coupling between components.

**Files:**
- `event_dispatcher.py` - Event dispatching infrastructure
- `event_args.py` - Custom event argument classes

**Key Responsibilities:**
- EventDispatcher registers and unregisters listeners, dispatches events to registered callbacks, and maintains the listener registry.
- Event argument classes (AccessEventArgs, AlertEventArgs, SuspiciousBehaviorEventArgs) encapsulate event data in structured objects.

**Design Pattern:** This module implements the Observer pattern (also known as Publish-Subscribe), enabling components to react to events without tight coupling. The AccessController publishes events without knowing specifically which objects will handle them, and SecurityManager subscribes to events without the AccessController needing to know about SecurityManager.

### src/files/ - File Operations

**Purpose:** Provides abstraction for file system operations including logging, JSON, and CSV handling.

**Files:**
- `file_manager.py` - File operations abstraction

**Key Responsibilities:**
- Log file writing and reading
- JSON import/export with validation
- CSV import/export
- Database backup and restore

**File Formats Used:**
- `.log` files for system logging
- `.json` files for data import/export
- `.csv` files for tabular data export
- `.db` files for SQLite database

### src/models/ - Data Models

**Purpose:** Defines the data model classes that represent core business entities.

**Files:**
- `user.py` - User model
- `access_log.py` - Access log model
- `alert.py` - Alert model

**Key Responsibilities:**
- Each model class encapsulates data and behavior related to a business entity
- Provides serialization to dictionaries (to_dict())
- Provides deserialization from dictionaries (from_dict())
- Implements meaningful string representations (__repr__)

**Design Pattern:** These classes follow the Data Transfer Object (DTO) pattern, encapsulating data in structured objects that can be passed between layers. They are plain Python objects without business logic, acting as data containers.

### src/analysis.py - Statistical Analysis

**Purpose:** Provides LINQ-style data analysis functions using Python functional programming patterns.

**Key Responsibilities:**
- Access pattern analysis using map/filter/reduce
- Peak hour detection
- Anomaly detection
- Report generation

**Functions:**
- `analyze_access_patterns()` - Aggregates access statistics
- `get_peak_access_hours()` - Identifies busiest access times
- `detect_anomalies()` - Finds statistical outliers
- `generate_access_report()` - Combined reporting

This module demonstrates LINQ-style patterns in Python, using list comprehensions, map(), filter(), reduce(), sorted(), and defaultdict for grouping.

### src/seed_data.py - Sample Data Generation

**Purpose:** Generates sample data for testing and development.

**Functionality:**
- Creates 20 sample users across 5 departments
- Generates 120 access logs with various patterns
- Simulates both normal and suspicious access behavior

The generated data includes patterns designed to train the AI model effectively: approximately 15% of access attempts occur during nighttime hours (suspicious), 10% involve high frequency within short time windows (suspicious), and 15% involve non-assigned rooms (potentially suspicious). This deliberate distribution ensures the training data contains sufficient examples of each classification category.

### src/cli.py - Command-Line Interface

**Purpose:** Provides a terminal-based interface for interacting with the system.

**Key Responsibilities:**
- User management commands
- Access log management commands
- Access request simulation
- Alert viewing

The CLI serves developers and administrators who prefer command-line interfaces, enabling testing and system administration without the web interface.

## 2.3 Presentation Layer

### templates/ - Flask Templates

The Flask web application uses Jinja2 templates for rendering HTML pages. Templates include:

- `base.html` - Base template with common layout
- `index.html` - Home page
- `dashboard.html` - System dashboard with statistics
- `users.html` - User management interface
- `access_logs.html` - Access log viewer
- `alerts.html` - Security alert viewer
- `request_access.html` - Access request form
- `access_result.html` - Access result display

### tests/ - Test Suite

The project includes comprehensive unit and integration tests covering:

- `test_analyzer.py` - AI component tests
- `test_database.py` - Database operation tests
- `test_events.py` - Event system tests
- `test_models.py` - Model tests
- `test_controllers.py` - Controller tests
- `test_file_manager.py` - File operation tests
- `test_integration.py` - End-to-end workflow tests
- `test_cli.py` - CLI tests

---

# 3. Application Startup Flow

## 3.1 Startup Sequence

The Flask application (`app.py`) follows a specific initialization sequence when started:

### Step 1: Flask Application Creation
```
app = Flask(__name__)
```
The Flask application instance is created, which initializes the web framework and configures template rendering.

### Step 2: Database Initialization
```
db = DatabaseManager("access_control.db")
```
The DatabaseManager is instantiated with the database file path. Upon creation, it connects to the SQLite database. Note that the code does not call `init_db()` explicitly here, as the web application assumes the database has been initialized through other means (seed_data.py or CLI initialization).

### Step 3: Event System Initialization
```
dispatcher = EventDispatcher()
```
The EventDispatcher is instantiated. This is the central hub for event-driven communication.

### Step 4: AI Model Initialization
```
analyzer = BehaviorAnalyzer(db)
```
The BehaviorAnalyzer is instantiated with a reference to the database manager.

### Step 5: Model Loading/Training
```
if not analyzer.is_trained:
    try:
        analyzer.train_from_database()
    except:
        pass
```
The analyzer checks if a trained model exists. If not (the default state), it attempts to train from existing access logs in the database. The exception handling ensures the application starts even if training fails (insufficient data, database errors, etc.).

### Step 6: Controller Instantiation
```
access_controller = AccessController(db, dispatcher)
security_manager = SecurityManager(db, dispatcher)
```
The controllers are instantiated with dependencies. This is a form of dependency injection: the database and event dispatcher are passed to controllers rather than having controllers create their own dependencies.

### Step 7: Event Listener Registration
```
dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)
dispatcher.register_listener("on_multiple_attempts", security_manager.on_multiple_attempts_handler)
```
The SecurityManager registers its handler methods as listeners for security-related events. This establishes the Observer pattern relationships.

### Step 8: Route Registration
```
@app.route('/')
def index():
    return render_template('index.html')
# ... additional routes
```
Flask decorators register the various routes that handle HTTP requests.

## 3.2 Initialization Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        START                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Flask(__name__)                                                │
│  - Create Flask application                                      │
│  - Configure Jinja2 templates                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DatabaseManager("access_control.db")                           │
│  - Connect to SQLite database                                   │
│  - Configure row factory forsqlite3.Row                        │
│  (Note: init_db() skipped in web app - assumes pre-initialized)│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  EventDispatcher()                                               │
│  - Initialize empty listener dictionary                           │
│  - Prepare for event registration                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  BehaviorAnalyzer(db)                                          │
│  - Create DecisionTreeClassifier                               │
│  - Initialize untrained model                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  analyzer.train_from_database()                                │
│  - Query all access logs from database                         │
│  - Extract features and labels                                   │
│  - Train classifier                                             │
│  - Set is_trained = True                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
           ┌─────────────────────────────��┬��─────────────────────┐
           │                              │                      │
           ▼                              ▼                      ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│ Training Failed │        │ Training       │        │ No Data         │
│ (Exception)     │        │ Successful     │        │ (Empty DB)      │
└─────────────────┘        └─────────────────┘        └─────────────────┘
           │                              │                      │
           └──────────────────────────────┴──────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  AccessController(db, dispatcher)                               │
│  SecurityManager(db, dispatcher)                               │
│  - Inject dependencies                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  register_listener()                                           │
│  - SecurityManager subscribes to:                                │
│    • on_suspicious_behavior                                     │
│    • on_access_denied                                           │
│    • on_multiple_attempts                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  @app.route() decorators                                        │
│  - Register HTTP request handlers                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  app.run(debug=True)                                            │
│  - Start development server                                    │
│  - Listen for HTTP requests                                    │
└─────────────────────────────────────────────────────────────────┘
```

## 3.3 Alternative Startup Paths

The system supports multiple startup paths depending on use case:

### CLI Startup (`python src/cli.py`)
The CLI provides an alternative interface that initializes similarly but stores the database in a different location (under the `data/` directory) and supports different interaction patterns.

### Seed Data Generation (`python -m src.seed_data`)
The seed_data module can be run independently to initialize a fresh database with sample data, including:
- 20 users across 5 departments
- 120 access logs with mixed patterns
- Both normal and suspicious access attempts

This is the primary initialization method for new deployments.

---

# 4. Full Class Documentation

## 4.1 Data Model Classes

### User (src/models/user.py)

**File Location:** `src/models/user.py`

**Purpose:** Represents a system user who can attempt access to physical locations.

**Class Definition:**
```python
class User:
    def __init__(self, id=None, name=None, department=None, access_level=1, assigned_room=None):
        self.id = id
        self.name = name
        self.department = department
        self.access_level = access_level
        self.assigned_room = assigned_room
```

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| id | int or None | Primary key identifier; None for new users before insertion |
| name | str or None | User's full name |
| department | str or None | Department identifier (IT, HR, Finance, Marketing, Operations) |
| access_level | int | Access authorization level (1-5, default 1) |
| assigned_room | str or None | Primary assigned location (e.g., "IT-101") |

**Important Methods:**

`to_dict()` - Converts User to dictionary representation
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'department': self.department,
        'access_level': self.access_level,
        'assigned_room': self.assigned_room
    }
```
Returns a dictionary containing all user attributes, suitable for JSON serialization or database operations.

`from_dict(cls, data)` - Creates User from dictionary
```python
@classmethod
def from_dict(cls, data):
    return cls(
        id=data.get('id'),
        name=data.get('name'),
        department=data.get('department'),
        access_level=data.get('access_level', 1),
        assigned_room=data.get('assigned_room')
    )
```
Factory method that creates a User instance from a dictionary, using `.get()` with defaults for optional fields.

**Relationships:**
- User objects are created, read, updated, and deleted through DatabaseManager
- User IDs are referenced in AccessLog and Alert objects as foreign keys
- User information is passed to BehaviorAnalyzer for feature extraction

**Serialization Example:**
```python
# Creating a user
user = User(name="Alice Johnson", department="IT", access_level=3, assigned_room="IT-101")

# Serializing to dictionary
user_dict = user.to_dict()
# {'id': None, 'name': 'Alice Johnson', 'department': 'IT', 
#  'access_level': 3, 'assigned_room': 'IT-101'}

# Deserializing from dictionary
user2 = User.from_dict({'name': 'Bob Smith', 'department': 'HR'})
# User(id=None, name="Bob Smith", department="HR", access_level=1, assigned_room=None)
```

---

### AccessLog (src/models/access_log.py)

**File Location:** `src/models/access_log.py`

**Purpose:** Represents a single access attempt, whether granted or denied.

**Class Definition:**
```python
class AccessLog:
    def __init__(self, id=None, user_id=None, access_time=None, location=None, status='granted', attempts_count=1):
        self.id = id
        self.user_id = user_id
        self.access_time = access_time
        self.location = location
        self.status = status
        self.attempts_count = attempts_count
```

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| id | int or None | Primary key identifier |
| user_id | int or None | Foreign key to users table |
| access_time | str or None | ISO format timestamp (e.g., "2024-01-15T14:30:00") |
| location | str or None | Requested access location |
| status | str | Either 'granted' or 'denied' |
| attempts_count | int | Number of attempts in this log entry (default 1) |

**Important Methods:**

`to_dict()` - Converts AccessLog to dictionary
```python
def to_dict(self):
    return {
        'id': self.id,
        'user_id': self.user_id,
        'access_time': self.access_time,
        'location': self.location,
        'status': self.status,
        'attempts_count': self.attempts_count
    }
```

`from_dict(cls, data)` - Creates AccessLog from dictionary
```python
@classmethod
def from_dict(cls, data):
    return cls(
        id=data.get('id'),
        user_id=data.get('user_id'),
        access_time=data.get('access_time'),
        location=data.get('location'),
        status=data.get('status', 'granted'),
        attempts_count=data.get('attempts_count', 1)
    )
```

**Design Notes:**
The `status` field is intentionally a string rather than a boolean to allow for potential expansion to additional states in the future (e.g., "pending", "expired"). The default of 'granted' reflects the optimistic nature of access control logging: most attempts are successful.

---

### Alert (src/models/alert.py)

**File Location:** `src/models/alert.py`

**Purpose:** Represents a security alert generated by the system in response to suspicious activity.

**Class Definition:**
```python
class Alert:
    def __init__(self, id=None, user_id=None, alert_type=None, description=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.alert_type = alert_type
        self.description = description
        self.created_at = created_at
```

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| id | int or None | Primary key identifier |
| user_id | int or None | Foreign key to users table |
| alert_type | str or None | Type of alert (suspicious_behavior, access_denied, multiple_attempts) |
| description | str or None | Human-readable description of the alert |
| created_at | str or None | ISO format timestamp |

**Important Methods:**
Standard `to_dict()` and `from_dict()` methods follow the same pattern as User and AccessLog.

**Alert Types:**
| Type | Description |
|------|-------------|
| suspicious_behavior | AI model classified behavior as suspicious |
| access_denied | Access was denied for any reason |
| multiple_attempts | User exceeded failed attempt threshold |

---

## 4.2 Event System Classes

### EventDispatcher (src/events/event_dispatcher.py)

**File Location:** `src/events/event_dispatcher.py`

**Purpose:** Implements the Observer pattern for event-driven communication between components.

**Class Definition:**
```python
class EventDispatcher:
    def __init__(self):
        self._listeners = {}
```

**Architecture:** The EventDispatcher maintains a dictionary where keys are event type strings and values are lists of callback functions.

**Important Methods:**

`register_listener(self, event_type, callback)` - Subscribe to an event
```python
def register_listener(self, event_type, callback):
    if event_type not in self._listeners:
        self._listeners[event_type] = []
    if callback not in self._listeners[event_type]:
        self._listeners[event_type].append(callback)
```
Multiple listeners can register for the same event type. The method prevents duplicate registrations. This is important because registering the same handler twice would result in duplicate alerts.

`unregister_listener(self, event_type, callback)` - Unsubscribe from an event
```python
def unregister_listener(self, event_type, callback):
    if event_type in self._listeners:
        if callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
```
Clean removal of listeners when they are no longer needed.

`dispatch_event(self, event_type, event_args)` - Fire an event
```python
def dispatch_event(self, event_type, event_args):
    if event_type in self._listeners:
        for callback in self._listeners[event_type]:
            callback(event_args)
```
Iterates through all registered listeners for the event type and invokes each callback with the event arguments. Listeners are invoked in registration order.

`get_listeners(self, event_type)` - Query registered listeners
```python
def get_listeners(self, event_type):
    return self._listeners.get(event_type, [])
```
Utility method for debugging and introspection.

**Event Types:**
| Event Type | When Fired | Data Structure |
|-----------|-----------|--------------|
| on_suspicious_behavior | AI classifies behavior as suspicious | SuspiciousBehaviorEventArgs |
| on_access_denied | Access is denied | AccessEventArgs |
| on_multiple_attempts | User has >3 failed attempts in time window | AlertEventArgs |

**Usage Example:**
```python
# Creating dispatcher
dispatcher = EventDispatcher()

# Registering a handler
def my_handler(event_args):
    print(f"Event received: {event_args.user_id}")

dispatcher.register_listener("on_suspicious_behavior", my_handler)

# Later, dispatching an event
from src.events.event_args import SuspiciousBehaviorEventArgs
event = SuspiciousBehaviorEventArgs(user_id=1, score=0.85, reason="Night access", timestamp="2024-01-15T03:00:00")
dispatcher.dispatch_event("on_suspicious_behavior", event)
# Output: "Event received: 1"
```

---

### Event Argument Classes (src/events/event_args.py)

**Purpose:** Encapsulate event data in structured objects that can be passed to event handlers.

#### AccessEventArgs

```python
class AccessEventArgs:
    def __init__(self, user_id, location, reason, timestamp):
        self.user_id = user_id
        self.location = location
        self.reason = reason
        self.timestamp = timestamp
```

Used when access is denied or when notifying about access attempts. Contains the user ID, requested location, reason for the event, and timestamp.

#### AlertEventArgs

```python
class AlertEventArgs:
    def __init__(self, user_id, alert_type, description, created_at):
        self.user_id = user_id
        self.alert_type = alert_type
        self.description = description
        self.created_at = created_at
```

Used for general alerts, particularly for the "on_multiple_attempts" event. Contains alert type, description, and creation timestamp.

#### SuspiciousBehaviorEventArgs

```python
class SuspiciousBehaviorEventArgs:
    def __init__(self, user_id, score, reason, timestamp):
        self.user_id = user_id
        self.score = score
        self.reason = reason
        self.timestamp = timestamp
```

Most detailed event args, used specifically for "on_suspicious_behavior" events. Includes the AI classification score (0-1) indicating confidence of suspicious activity.

**Common Pattern:** Each event args class implements `to_dict()` converting all attributes to a dictionary, useful for logging, JSON export, and debugging.

---

## 4.3 Database Classes

### DatabaseManager (src/database/database_manager.py)

**File Location:** `src/database/database_manager.py`

**Purpose:** Provides complete database abstraction, handling all SQLite operations.

**Class Definition:**
```python
class DatabaseManager:
    def __init__(self, db_path="access_control.db"):
        self.db_path = db_path
        self.connection = None
        self.connect()
```

**Key Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| db_path | str | Path to SQLite database file |
| connection | sqlite3.Connection | Active database connection |

**Core Methods:**

`connect()` - Establish database connection
```python
def connect(self):
    self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
    self.connection.row_factory = sqlite3.Row
```
The `check_same_thread=False` parameter allows multi-threaded access (necessary for Flask's threaded mode). The row_factory is set to `sqlite3.Row` to enable dictionary-style access to query results.

`init_db()` - Create database schema
```python
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
    
    # Similar for access_logs and alerts tables
    self.connection.commit()
```
Creates all three tables with appropriate constraints and foreign keys if they don't exist.

**CRUD Operations - Users:**

`create_user(user)` - Insert new user
```python
def create_user(self, user):
    cursor = self.connection.cursor()
    cursor.execute(
        'INSERT INTO users (name, department, access_level, assigned_room) VALUES (?, ?, ?, ?)',
        (user.name, user.department, user.access_level, user.assigned_room)
    )
    self.connection.commit()
    return cursor.lastrowid
```
Uses parameterized queries to prevent SQL injection. Returns the new user's ID.

`get_user(user_id)` - Retrieve single user
```python
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
```
Returns None if user not found (missing user is not an error condition).

`get_all_users()` - Retrieve all users
```python
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
```
Uses list comprehension for concise mapping of database rows to objects.

`update_user(user_id, **kwargs)` - Update user fields
```python
def update_user(self, user_id, **kwargs):
    fields = ', '.join(f'{key} = ?' for key in kwargs.keys())
    values = list(kwargs.values())
    values.append(user_id)
    cursor = self.connection.cursor()
    cursor.execute(f'UPDATE users SET {fields} WHERE id = ?', values)
    self.connection.commit()
    return cursor.rowcount > 0
```
Dynamic field update allowing any subset of fields to be updated. Returns whether any rows were affected.

`delete_user(user_id)` - Delete user
```python
def delete_user(self, user_id):
    cursor = self.connection.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    self.connection.commit()
    return cursor.rowcount > 0
```

**Equivalent CRUD operations exist for AccessLog and Alert:**

| Operation | Users | Access Logs | Alerts |
|-----------|-------|------------|--------|
| Create | create_user() | create_access_log() | create_alert() |
| Read (single) | get_user() | get_access_log() | get_alert() |
| Read (all) | get_all_users() | get_all_access_logs() | get_all_alerts() |
| Read (user scoped) | N/A | get_user_access_logs() | get_user_alerts() |
| Update | update_user() | N/A | N/A |
| Delete | delete_user() | delete_access_log() | delete_alert() |

**Advanced Query Methods:**

`get_user_access_count(user_id)` - Count user's total access attempts
```python
def get_user_access_count(self, user_id):
    cursor = self.connection.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM access_logs WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    return row['count'] if row else 0
```

`get_user_access_count_by_status(user_id, status)` - Count by status
```python
def get_user_access_count_by_status(self, user_id, status):
    cursor = self.connection.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM access_logs WHERE user_id = ? AND status = ?', (user_id, status))
    row = cursor.fetchone()
    return row['count'] if row else 0
```

`get_location_access_count(location)` - Count accesses to a location
```python
def get_location_access_count(self, location):
    cursor = self.connection.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM access_logs WHERE location = ?', (location,))
    row = cursor.fetchone()
    return row['count'] if row else 0
```

`get_department_access_stats(department)` - Get access statistics by department
```python
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
```
Demonstrates SQL aggregation with conditional counting.

`get_access_logs_by_date_range(start_date, end_date)` - Query by date range
```python
def get_access_logs_by_date_range(self, start_date, end_date):
    cursor = self.connection.cursor()
    cursor.execute(
        'SELECT * FROM access_logs WHERE access_time >= ? AND access_time <= ?',
        (start_date, end_date)
    )
    # Convert to AccessLog objects
```

`get_most_active_users(limit=10)` - Find most active users
```python
def get_most_active_users(self, limit=10):
    cursor = self.connection.cursor()
    cursor.execute('''
        SELECT user_id, COUNT(*) as access_count
        FROM access_logs
        GROUP BY user_id
        ORDER BY access_count DESC
        LIMIT ?
    ''', (limit,))
    # Return [{user_id, access_count}, ...]
```

`get_suspicious_users(days=7)` - Find users with multiple denials
```python
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
    # Return suspicious users
```

---

## 4.4 Controller Classes

### AccessController (src/controllers/access_controller.py)

**File Location:** `src/controllers/access_controller.py`

**Purpose:** Orchestrates access request processing by coordinating with the AI analyzer and event system.

**Class Definition:**
```python
class AccessController:
    def __init__(self, database, event_dispatcher):
        self.database = database
        self.event_dispatcher = event_dispatcher
        self.analyzer = BehaviorAnalyzer(database)
```

**Key Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| database | DatabaseManager | Database access layer |
| event_dispatcher | EventDispatcher | Event system |
| analyzer | BehaviorAnalyzer | AI component for classification |

**Important Methods:**

`request_access(user_id, location, access_time=None)` - Process access request
This is the primary method that handles access requests. The processing flow:

1. **Time normalization:** If no access_time provided, use current time. Convert to ISO format string.

2. **User validation:** Retrieve user from database. If not found, return denial with "User not found" reason.

3. **AI analysis (if trained):**
   - Call analyzer.analyze() to get classification
   - If classification is "Suspicious", trigger on_suspicious_behavior event and deny access
   - If classification is "Normal", grant access

4. **Fallback rules (if not trained):**
   - If requested location matches assigned_room, grant
   - If location starts with user's department, grant
   - Otherwise, deny

5. **Event dispatch:** For deny operations, dispatch on_access_denied event

**Processing Flow Diagram:**
```
request_access(user_id, location)
         │
         ▼
┌─────────────────────┐
│ Validate user      │
│ exists?          │
└─────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
Found     Not Found
    │         │
    ▼         ▼
┌──────────────┐    ┌───────────────────┐
│ Analyzer   │    │ Deny: User       │
│ trained?   │    │ not found        │
└──────────────┘    └───────────────────┘
    │
    ├────────────┬────────────┐
    │          │          │
    ▼          ▼          ▼
 Yes        No        Error
    │          │          │
    ▼          ▼          ▼
┌──────────────┐    ┌───────────────────┐
│ Call       │    │ Fallback         │
│ analyzer.  │    │ rules           │
│ analyze()  │    │                │
└──────────────┘    └───────────────────┘
    │
    ├────────────┬────────────┐
    │          │          │
    ▼          ▼          ▼
Normal    Suspicious    Error
    │          │          │
    ▼          ▼          ▼
┌──────────────┐    ┌───────────────────┐
│ Grant       │    �� Dispatch         │
│ access     │    │ on_suspicious    │
│ + log      │    │ behavior event   │
│            │    │ + deny access   │
└──────────────┘    └───────────────────┘
```

`grant_access(user_id, location, access_time)` - Grant and log access
Creates an AccessLog with status='granted', saves to database, returns success response.

`deny_access(user_id, location, reason, access_time)` - Deny and log access
Creates an AccessLog with status='denied', saves to database, dispatches on_access_denied event, returns denial response.

`grant_access_with_analysis(user_id, location, access_time, analysis)` - Grant with AI data
Similar to grant_access but includes classification and confidence scores from AI analysis in the response.

**Response Format:**
```python
{
    'granted': True/False,
    'classification': 'Normal'/'Suspicious',
    'confidence_normal': 0-100,
    'confidence_suspicious': 0-100,
    'reason': 'Human-readable reason',
    'user_id': int,
    'location': str,
    'timestamp': str
}
```

**Relationship to Other Components:**
- AccessController uses DatabaseManager to persist access logs and read user data
- AccessController uses BehaviorAnalyzer for AI classification
- AccessController uses EventDispatcher to notify about security events
- SecurityManager listens to events dispatched by AccessController

---

### SecurityManager (src/controllers/security_manager.py)

**File Location:** `src/controllers/security_manager.py`

**Purpose:** Handles security events, creates alerts, and monitors for repeated failed access attempts.

**Class Definition:**
```python
class SecurityManager:
    def __init__(self, database, event_dispatcher, file_manager=None):
        self.database = database
        self.event_dispatcher = event_dispatcher
        self.file_manager = file_manager
```

**Key Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| database | DatabaseManager | Database access layer |
| event_dispatcher | EventDispatcher | Event system |
| file_manager | FileManager or None | Optional file logging |

**Important Methods:**

`handle_alert(event_args)` - Generic alert handler
Processes alert events by creating Alert records in the database and optionally writing to log files.

```python
def handle_alert(self, event_args):
    alert = Alert(
        user_id=event_args.user_id,
        alert_type=event_args.alert_type,
        description=event_args.description,
        created_at=event_args.created_at
    )
    self.database.create_alert(alert)
    if self.file_manager:
        self.file_manager.write_log(f"Alert: {event_args.alert_type} - {event_args.description}")
```

`on_suspicious_behavior_handler(event_args)` - Handler for suspicious behavior events
Specific handler registered for "on_suspicious_behavior" events:

```python
def on_suspicious_behavior_handler(self, event_args):
    if isinstance(event_args, SuspiciousBehaviorEventArgs):
        alert = Alert(
            user_id=event_args.user_id,
            alert_type='suspicious_behavior',
            description=f"Suspicious behavior detected: {event_args.reason} (score: {event_args.score})",
            created_at=event_args.timestamp
        )
        self.database.create_alert(alert)
        if self.file_manager:
            self.file_manager.write_log(f"Suspicious behavior: User {event_args.user_id} - {event_args.reason}")
```

The method handles both direct SuspiciousBehaviorEventArgs objects and objects with compatible attributes (duck typing).

`on_access_denied_handler(event_args)` - Handler for access denied events
```python
def on_access_denied_handler(self, event_args):
    self.log_denied_access(
        event_args.user_id,
        event_args.location,
        event_args.reason,
        event_args.timestamp
    )
```

`on_multiple_attempts_handler(event_args)` - Handler for multiple attempts events
```python
def on_multiple_attempts_handler(self, event_args):
    alert = Alert(
        user_id=event_args.user_id,
        alert_type='multiple_attempts',
        description=event_args.description,
        created_at=event_args.created_at
    )
    self.database.create_alert(alert)
```

`monitor_failed_attempts(user_id, time_window_minutes=60)` - Check for repeated failures
```python
def monitor_failed_attempts(self, user_id, time_window_minutes=60):
    all_logs = self.database.get_user_access_logs(user_id)
    cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
    
    recent_denied = []
    for log in all_logs:
        # Parse log time
        # Check if within window and denied
        pass
    
    is_suspicious = len(recent_denied) > 3
    
    if is_suspicious:
        # Dispatch on_multiple_attempts event
    
    return {'is_suspicious': is_suspicious, 'attempts_count': count, 'time_window': window}
```

This method can be called independently to check for suspicious access patterns. The 3-attempt threshold within 60 minutes triggers the multiple_attempts alert.

---

## 4.5 AI Component Classes

### BehaviorAnalyzer (src/ai/analyzer.py)

**File Location:** `src/ai/analyzer.py`

**Purpose:** Provides AI-powered behavior classification for detecting suspicious access patterns.

This is the most complex class in the system. Detailed in Section 7.

---

## 4.6 File Handling Classes

### FileManager (src/files/file_manager.py)

**File Location:** `src/files/file_manager.py`

**Purpose:** Provides abstraction for file system operations including logging, JSON, and CSV handling.

This class is detailed in Section 8.

---

# 5. Object Communication & Architecture

## 5.1 Communication Patterns

The system uses multiple communication patterns to enable loose coupling between components:

### Direct Method Calls (Synchronous)

The primary pattern where components directly invoke methods on other components:

```python
# In app.py
access_controller = AccessController(db, dispatcher)
security_manager = SecurityManager(db, dispatcher)

# AccessController calls DatabaseManager directly
user = self.database.get_user(user_id)

# AccessController creates AI analyzer internally
self.analyzer = BehaviorAnalyzer(database)
analysis = self.analyzer.analyze(...)
```

### Observer Pattern (Event-Driven)

Components subscribe to events and react when events are dispatched:

```python
# In app.py - registration
dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)

# Later - dispatch
dispatcher.dispatch_event('on_suspicious_behavior', event_args)
```

This pattern decouples the event publisher (AccessController) from subscribers (SecurityManager), allowing new handlers to be added without modifying AccessController.

### Dependency Injection

Components receive their dependencies through constructors rather than creating them:

```python
# AccessController receives database and dispatcher
access_controller = AccessController(db, dispatcher)

# Internal dependencies are also injected via construction
self.analyzer = BehaviorAnalyzer(database)  # Created within, but could be injected
```

## 5.2 Call Flow: Access Request

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        USER REQUESTS ACCESS                                │
└───────────────────────��─��────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Flask Route: /request_access                                            │
│  - Receives POST with user_id and location                                 │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  AccessController.request_access(user_id, location)                          │
└───────────────────────────────────────────���──────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Step 1: Get current timestamp                                          │
│  access_time = datetime.now().isoformat()                                 │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Step 2: Verify user exists                                             │
│  user = database.get_user(user_id)                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                            ┌───────┴───────┐
                            │               │
                            ▼               ▼
                    User Found         User Not Found
                            │               │
                            ▼               ▼
                    ┌───────────┐   ┌─────────────────────┐
                    │ Continue │   │ Return: denied    │
                    │ with    │   │ "User not found" │
                    │ analysis│   └─────────────────────┘
                    └───────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Step 3: AI Analysis                                                   │
│  analysis = analyzer.analyze(user_id, access_time, location)                  │
│                                                                       │
│  Extracts 10 features:                                                │
│  - hour, minute, day_of_week, is_weekend                                │
│  - access_count_last_hour                                               │
│  - is_assigned_room, is_same_department                                  │
│  - user_access_level, historical_denied_count                              │
│  - is_night_access                                                   │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Step 4: Classification                                               │
│  prediction = model.predict(feature_array)                             │
│  confidence = model.predict_proba(feature_array)                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                            ┌───────┴───────┐
                            │               │
                            ▼               ▼
                   Classification     Classification
                   = "Normal"        = "Suspicious"
                            │               │
                            ▼               ▼
              ┌──────────────────┐    ┌────────────────────────────────┐
              │ Grant access   │    │ Trigger event: on_suspicious     │
              │ - Create log │    │ behavior                       │
              │ - Return    │    │ dispatcher.dispatch_event(    │
              │   granted   │    │   'on_suspicious_behavior',    │
              └─────────────┘    │   EventArgs)                 │
                               └────────────────────────────────┘
                                    │
                                    ▼
              ┌────────────────────────────────┐
              │ SecurityManager handles       │
              │ on_suspicious_behavior     │
              │ - Creates Alert record     │
              │ - write_log() if file   │
              │   manager available    │
              └────────────────────────┘
```

## 5.3 Architecture Layers

The system follows a layered architecture:

| Layer | Responsibility | Components |
|-------|--------------|------------|
| Presentation | HTTP handling, UI rendering | Flask routes, templates |
| Application | Business logic orchestration | AccessController, SecurityManager |
| Intelligence | AI/ML classification | BehaviorAnalyzer |
| Data Access | Database operations | DatabaseManager |
| Utilities | File operations, events | FileManager, EventDispatcher |
| Models | Data structures | User, AccessLog, Alert |

Data flows downward through layers (HTTP request), and responses flow upward (classifications, alerts). Events can flow laterally within the application layer.

## 5.4 Module Dependencies

```
┌────────────────────────────────────────────────────────────────────────┐
│                           app.py                                      │
│  - Flask application                                                 │
│  - Initializes all components                                        │
└────────────────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬───────────┐
        ▼           ▼           ▼           ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────┐
│ Database │ │ Dispatch │ │Analyzer │ │   Templates  │
│ Manager  │ │ er       │ │(AI)     │ │              │
└──────���─���──┘ └───────────┘ └───────────┘ └───────────────┘
        │           │           │
    ┌───┴───┐   ┌───┴───┐   ┌───┴───────┐
    ▼       ▼   ▼       ▼   ▼           ▼
┌───────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐
│User   │ │AccessLog │ │Alert     │ │Security   │
│Model  │ │Model    │ │Model    │ │Manager    │
└───────┘ └───────────┘ └───────────┘ └─────────────┘
                    │               │
                    ▼               ▼
            ┌───────────┐ ┌──────────────────┐
            │Access    │ │FileManager     │
            │Controller│ │               │
            └─────────┘ └──────────────────┘
```

Note: FileManager is an optional dependency of SecurityManager, demonstrating composition over inheritance.

---

# 6. Database Analysis

## 6.1 Database Overview

The system uses SQLite, a lightweight, file-based relational database. SQLite was chosen because:

1. **Zero configuration:** No database server installation required
2. **Portability:** Single file can be copied between systems
3. **Simplicity:** Suited for single-user desktop applications
4. **Educational value:** Simple SQL syntax easy to understand
5. **Integration:** Well-supported in Python standard library

## 6.2 Schema Definition

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    access_level INTEGER NOT NULL DEFAULT 1,
    assigned_room TEXT
)
```

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier, auto-assigned |
| name | TEXT | NOT NULL | User's full name |
| department | TEXT | NOT NULL | Department (IT, HR, Finance, etc.) |
| access_level | INTEGER | NOT NULL, DEFAULT 1 | 1-5 access level |
| assigned_room | TEXT | None | Primary assigned location |

**Indexes:** Implicit primary key index on `id`

**Foreign Keys:** This table is referenced by:
- access_logs.user_id (foreign key)
- alerts.user_id (foreign key)

### Access Logs Table

```sql
CREATE TABLE access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    access_time TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT NOT NULL,
    attempts_count INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| user_id | INTEGER | NOT NULL, FK -> users.id | Reference to user |
| access_time | TEXT | NOT NULL | ISO timestamp |
| location | TEXT | NOT NULL | Requested location |
| status | TEXT | NOT NULL | 'granted' or 'denied' |
| attempts_count | INTEGER | DEFAULT 1 | Attempt count |

**Indexes:** Primary key on `id`, index on `user_id` (FK creates implicit index)

**Relationships:**
- Many-to-one with users (many logs per user)
- user_id is foreign key to users.id

**Status Values:**
- 'granted' - Access was permitted
- 'denied' - Access was not permitted

### Alerts Table

```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| user_id | INTEGER | NOT NULL, FK -> users.id | Reference to user |
| alert_type | TEXT | NOT NULL | Type of alert |
| description | TEXT | None | Alert details |
| created_at | TEXT | NOT NULL | ISO timestamp |

**Relationships:**
- Many-to-one with users
- user_id is foreign key to users.id

## 6.3 Entity-Relationship Diagram

```
┌─────────────────┐           ┌─────────────────┐
│     users      │           │  access_logs   │
├───────────────┤           ├───────────────┤
│ id (PK)      │◄──────────│ user_id (FK) │
│ name         │   1:N    │ id (PK)      │
│ department   │           │ access_time │
│ access_level │           │ location   │
│ assigned_room│           │ status     │
└─────────────┘           │ attempts  │
                          └───────────┘
                                │
                          ┌─────┴─────┐
                          │           │
                          ▼           ▼
                    ┌───────────┐   ┌─────────────┐
                    │  alerts  │   │           │
                    ├──────────┤   │           │
                    │ id (PK)  │   │           │
                    │ user_id  │◄──┘           │
                    │ alert_   │   │           │
                    │ type    │   │           │
                    │ descrip │   │           │
                    │ created │   │           │
                    │ _at     │   │           │
                    └─────────┘   │           │
                         ◄────────┘           │
                         1:N                 │
                    ┌─────────┐             │
                    │ users  │◄─────────────┘
                    └─────────┘
```

## 6.4 CRUD Operations

### Users

| Operation | SQL | Method |
|-----------|-----|--------|
| Create | INSERT INTO users... | create_user() |
| Read | SELECT * FROM users WHERE id=? | get_user() |
| Read All | SELECT * FROM users | get_all_users() |
| Update | UPDATE users SET... | update_user() |
| Delete | DELETE FROM users WHERE id=? | delete_user() |

### Access Logs

| Operation | SQL | Method |
|-----------|-----|--------|
| Create | INSERT INTO access_logs... | create_access_log() |
| Read | SELECT * FROM access_logs WHERE id=? | get_access_log() |
| Read All | SELECT * FROM access_logs | get_all_access_logs() |
| Read by User | SELECT * FROM access_logs WHERE user_id=? | get_user_access_logs() |
| Delete | DELETE FROM access_logs WHERE id=? | delete_access_log() |

### Alerts

| Operation | SQL | Method |
|-----------|-----|--------|
| Create | INSERT INTO alerts... | create_alert() |
| Read | SELECT * FROM alerts WHERE id=? | get_alert() |
| Read All | SELECT * FROM alerts | get_all_alerts() |
| Read by User | SELECT * FROM alerts WHERE user_id=? | get_user_alerts() |
| Delete | DELETE FROM alerts WHERE id=? | delete_alert() |

## 6.5 Example Records

### users table

| id | name | department | access_level | assigned_room |
|----|------|------------|--------------|--------------|
| 1 | Alice Johnson | IT | 3 | IT-101 |
| 2 | Bob Smith | HR | 2 | HR-201 |
| 3 | Charlie Brown | Finance | 4 | FIN-301 |
| 4 | Diana Prince | Marketing | 2 | MKT-401 |
| 5 | Eve Wilson | Operations | 5 | OPS-501 |

### access_logs table

| id | user_id | access_time | location | status | attempts_count |
|----|--------|------------|----------|--------|--------------|
| 1 | 1 | 2024-01-15T09:30:00 | IT-101 | granted | 1 |
| 2 | 1 | 2024-01-15T14:15:00 | FIN-301 | denied | 1 |
| 3 | 2 | 2024-01-15T10:00:00 | HR-201 | granted | 1 |
| 4 | 3 | 2024-01-16T03:00:00 | FIN-301 | denied | 1 |
| 5 | 1 | 2024-01-16T09:45:00 | IT-101 | granted | 1 |

### alerts table

| id | user_id | alert_type | description | created_at |
|----|--------|-----------|------------|------------|------------|
| 1 | 3 | suspicious_behavior | Night access detected (score: 0.92) | 2024-01-16T03:00:00 |
| 2 | 1 | access_denied | FIN-301 not authorized | 2024-01-15T14:15:00 |
| 3 | 3 | multiple_attempts | 4 failed attempts in 60 minutes | 2024-01-16T03:15:00 |

---

# 7. AI / ML System Deep Analysis

## 7.1 AI Purpose and Problem Statement

The AI component solves the problem of detecting suspicious access behavior in an automated, scalable way. Without AI, access control systems typically use static rules (e.g., "allow access to assigned room only"), which can be circumvented by attackers who understand the rules. The AI component learns from historical access patterns to identify behavioral anomalies that might indicate security threats.

**The Classification Problem:**
Given a set of features describing an access attempt (time, location, user profile, access history), predict whether the attempt is Normal or Suspicious.

**Why Machine Learning?**
- Rule-based systems require explicitly listing all suspicious conditions
- ML can identify non-obvious patterns in data
- ML can adapt as access patterns change over time
- ML provides confidence scores for decisions

## 7.2 Model Type

The system uses **scikit-learn's DecisionTreeClassifier**, a classification algorithm that learns decision rules from training data.

### Why Decision Trees?

1. **Interpretability:** The school project requirement mandates that students explain the algorithm. Decision trees are among the most interpretable ML models - decisions can be traced through the tree manually.

2. **No preprocessing required:** Decision trees don't require feature scaling or normalization, simplifying the implementation.

3. **Handles mixed data types:** Can work with both categorical (department) and numerical (hour) features.

4. **Sufficient for project:** Decision trees can achieve good performance on this classification task given the feature set.

5. **Avoids black box:** Unlike neural networks, decision trees produce explicit rules.

### Alternative Models Considered

| Model | Pros | Cons | Decision |
|-------|------|------|----------|
| Decision Tree | Interpretable, simple | May overfit | **Selected** |
| Random Forest | More accurate | Less interpretable | - |
| Logistic Regression | Interpretable | Linear boundaries | - |
| Neural Network | High accuracy | Black box | - |
| Rule-based | Fully transparent | No learning | Adjunctive only |

## 7.3 Feature Engineering

The `extract_features()` method converts raw access request data into 10 numerical features:

### Feature List

| Feature | Type | Source | Description |
|---------|------|--------|-------------|
| hour | int | access_time | Hour of day (0-23) |
| minute | int | access_time | Minute of hour (0-59) |
| day_of_week | int | access_time | Day 0-6 (Monday-Sunday) |
| is_weekend | int | access_time | 1 if Saturday/Sunday |
| access_count_last_hour | int | database | Attempts in last 60 minutes |
| is_assigned_room | int | user.assigned_room | 1 if location matches assigned room |
| is_same_department | int | user.department | 1 if department prefix matches |
| user_access_level | int | user.access_level | User's authorization level |
| historical_denied_count | int | database | Previous denied attempts |
| is_night_access | int | hour | 1 if hour >= 22 or < 6 |

### Feature Extraction Code

```python
def extract_features(self, user_id, access_time, location):
    # Parse timestamp
    if isinstance(access_time, str):
        access_dt = datetime.fromisoformat(access_time.replace('Z', '+00:00'))
    else:
        access_dt = access_time

    hour = access_dt.hour
    minute = access_dt.minute
    day_of_week = access_dt.weekday()
    is_weekend = 1 if day_of_week >= 5 else 0

    # Frequency analysis
    access_count_last_hour = self.get_access_frequency(user_id, 60)

    # Location analysis
    user = self.database.get_user(user_id)
    if user:
        is_assigned = 1 if location == user.assigned_room else 0
        location_dept = location.split('-')[0] if '-' in location else location
        is_same_dept = 1 if location_dept == user.department else 0
        user_access_level = user.access_level
    else:
        is_assigned = 0
        is_same_dept = 0
        user_access_level = 1

    # Historical analysis
    historical_denied = self.get_historical_denied_count(user_id)
    is_night = 1 if self.is_night_access(hour) else 0

    return {
        'hour': hour,
        'minute': minute,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend,
        'access_count_last_hour': access_count_last_hour,
        'is_assigned_room': is_assigned,
        'is_same_department': is_same_dept,
        'user_access_level': user_access_level,
        'historical_denied_count': historical_denied,
        'is_night_access': is_night
    }
```

## 7.4 Training Data

### Data Source

Training data comes from the access_logs table in the database:

```python
def train_from_database(self):
    all_logs = self.database.get_all_access_logs()
```

### Label Generation (Ground Truth)

Since there's no human-labeled dataset, the system generates labels using heuristic rules:

```python
is_suspicious = 0
if features['is_night_access'] == 1:
    is_suspicious = 1
elif features['access_count_last_hour'] > 3:
    is_suspicious = 1
elif features['is_assigned_room'] == 0:
    is_suspicious = 1
```

This is a form of **semi-supervised** learning where the "teacher" is a rule-based system. The rules capture:

1. **Night access indicator:** Access during 22:00-06:00 is suspicious
2. **Frequency indicator:** More than 3 attempts/hour is suspicious
3. **Location indicator:** Accessing non-assigned room is suspicious

### Why This Approach?

- School project requirement prohibits "ready-made AI models" without adaptation
- Students understand the rules, so they can explain why suspicious = 1
- Rules can be verified against domain knowledge
- The model learns more nuanced patterns than the raw rules

### Training Data Distribution

Generated by seed_data.py:

- 120 total access logs
- ~15% night access (will be labeled suspicious)
- ~10% high frequency (will be suspicious)
- ~15% non-assigned room (will be suspicious)
- Some overlap between categories

## 7.5 Training Process

```python
def train_from_database(self):
    try:
        all_logs = self.database.get_all_access_logs()
        if not all_logs or len(all_logs) < 30:
            return {'error': 'Insufficient data. Need at least 30 access logs.'}

        X = []
        y = []

        for log in all_logs:
            try:
                features = self.extract_features(log.user_id, log.access_time, log.location)

                # Generate labels using rules
                is_suspicious = 0
                if features['is_night_access'] == 1:
                    is_suspicious = 1
                elif features['access_count_last_hour'] > 3:
                    is_suspicious = 1
                elif features['is_assigned_room'] == 0:
                    is_suspicious = 1

                X.append([feature vector])
                y.append(is_suspicious)
            except Exception:
                continue

        if len(X) < 30:
            return {'error': 'Insufficient valid samples for training.'}

        self.model.fit(X, y)
        self.is_trained = True

        accuracy = self.model.score(X, y)
        return {'num_samples': len(X), 'accuracy': accuracy}
```

Training steps:
1. Fetch all access logs from database
2. Validate minimum samples (30 required)
3. For each log, extract features
4. Generate ground truth label using rules
5. Collect X (features) and y (labels) lists
6. Fit model on X, y
7. Set is_trained flag
8. Return training statistics

## 7.6 Prediction Process

```python
def analyze(self, user_id, access_time, location):
    if not self.is_trained:
        return {'error': 'Model not trained. Call train_from_database() first.'}

    # Extract features
    features = self.extract_features(user_id, access_time, location)
    feature_array = [list of 10 features]

    # Get prediction
    prediction = self.model.predict([feature_array])[0]
    proba = self.model.predict_proba([feature_array])[0]

    # Get confidence
    confidence = self.get_prediction_confidence(features)

    # Translate prediction
    if prediction == 1:
        classification = "Suspicious"
        reason = self._generate_reason(features)
    else:
        classification = "Normal"
        reason = "Access pattern appears normal"

    return {
        'classification': classification,
        'confidence_normal': confidence['normal_prob'] * 100,
        'confidence_suspicious': confidence['suspicious_prob'] * 100,
        'reason': reason,
        'user_id': user_id,
        'location': location,
        'timestamp': access_time
    }
```

Prediction flow:
1. Check if model is trained
2. Extract 10 features from input
3. Convert to array format
4. Call model.predict() for classification
5. Call model.predict_proba() for probability estimates
6. Generate human-readable reason
7. Return structured result

## 7.7 Suspicious Behavior Detection Logic

The AI model detects suspicious behavior based on these criteria:

### Time Analysis

```python
def is_night_access(self, hour):
    return hour >= 22 or hour < 6
```

**Night hours:** 22:00 (10 PM) to 06:00 (6 AM)
- Rationale: Most legitimate access occurs during business hours
- Night access is unusual and warrants scrutiny
- Score contribution: If night, significantly increases suspicious probability

### Frequency Analysis

```python
def get_access_frequency(self, user_id, time_window_minutes=60):
    logs = self.database.get_user_access_logs(user_id)
    cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
    count = sum(1 for log in logs if log_time >= cutoff_time)
    return count
```

**High frequency threshold:** More than 3 attempts in 60 minutes
- Rationale: Normal users make 1-2 access attempts
- Rapid repeated attempts suggest credential sharing or brute-force
- Alert triggers: Dispatch on_multiple_attempts event

### Location Analysis

```python
# During feature extraction:
is_assigned = 1 if location == user.assigned_room else 0
is_same_dept = 1 if location_dept == user.department else 0
```

**Location validity:**
- Match to assigned_room: Direct authorization
- Match to department prefix: Department-level authorization
- Neither: Potentially unauthorized

### Historical Analysis

```python
def get_historical_denied_count(self, user_id):
    logs = self.database.get_user_access_logs(user_id)
    return sum(1 for log in logs if log.status == 'denied')
```

**Historical pattern:** Users with many denied attempts
- Rationale: Repeated denials may indicate probing attacks
- Threshold: More than 5 historical denials flagged

## 7.8 Confidence Scores

The model provides confidence scores using probability estimates:

```python
def get_prediction_confidence(self, features):
    feature_array = [features list]
    proba = self.model.predict_proba([feature_array])[0]
    return {
        'normal_prob': proba[0],
        'suspicious_prob': proba[1]
    }
```

`predict_proba()` returns the probability of each class:
- proba[0] = P(Normal)
- proba[1] = P(Suspicious)

These are scaled to percentages (0-100) for display.

## 7.9 Reason Generation

When classification is Suspicious, the system generates human-readable reasons:

```python
def _generate_reason(self, features):
    reasons = []
    if features['is_night_access'] == 1:
        reasons.append("Access during night hours (22:00-06:00)")
    if features['access_count_last_hour'] > 3:
        reasons.append(f"High access frequency ({count} attempts in last hour)")
    if features['is_assigned_room'] == 0:
        reasons.append("Accessing non-assigned room")
    if features['is_same_department'] == 0:
        reasons.append("Accessing different department area")
    if features['historical_denied_count'] > 5:
        reasons.append(f"User has {count} historical denied attempts")
    return "; ".join(reasons) if reasons else "Suspicious access pattern detected"
```

Multiple reasons are concatenated with "; ".

## 7.10 Model Serialization

The trained model can be saved and loaded for reuse:

```python
def save_model(self, filepath="model.pkl"):
    with open(filepath, 'wb') as f:
        pickle.dump({
            'model': self.model,
            'is_trained': self.is_trained
        }, f)

def load_model(self, filepath="model.pkl"):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
        self.model = data['model']
        self.is_trained = data['is_trained']
```

Uses Python's pickle module for serialization. The file contains both the model and training state.

## 7.11 Error Handling

### Insufficient Data

```python
if not all_logs or len(all_logs) < 30:
    return {'error': 'Insufficient data. Need at least 30 access logs.'}
```

Minimum 30 samples required for meaningful training.

### Model Not Trained

```python
if not self.is_trained:
    return {'error': 'Model not trained. Call train_from_database() first.'}
```

Falls back to basic rules if model unavailable.

### Exception Handling

All database operations are wrapped in try/except to prevent crashes:

```python
try:
    logs = self.database.get_user_access_logs(user_id)
except Exception:
    return 0
```

Returns default values on errors rather than propagating exceptions.

## 7.12 Model Limitations

### Known Limitations

1. **Training on Rules:** The model learns from rule-generated labels, so it can only learn patterns similar to the rules
2. **No True Anomaly Detection:** The model doesn't discover novel anomalies, only matches known patterns
3. **Small Dataset:** Only 120 training samples (minimum 30), limiting model complexity
4. **Imbalanced Classes:** Most access is normal, potentially biased toward Normal classification
5. **No Temporal Validation:** Uses full dataset rather than train/test split for validation
6. **Static Thresholds:** Thresholds (3 attempts, night hours) are hardcoded

### Weaknesses

- **False Positives:** Legitimate after-hours workers may be flagged
- **False Negatives:** Sophisticated attackers could avoid detection by mimicking normal patterns
- **No Adaptation:** Model doesn't retrain without explicit call to retrain()
- **No Feature Engineering:** Only uses provided features, no derived features

### Recommendations for Improvement

1. **Larger Dataset:** Generate more varied training data
2. **Cross-Validation:** Use proper train/test split
3. **Ensemble Methods:** Random Forest for better generalization
4. **Dynamic Thresholds:** Allow threshold configuration
5. **Online Learning:** Retrain periodically with new data

This section provides sufficient depth for school project defense. Students should understand:
- What features are used
- How training labels are generated
- How prediction works
- What the model can and cannot detect

---

# 8. File Handling System

## 8.1 FileManager Overview

The FileManager class (src/files/file_manager.py) provides a unified interface for file operations:

| Operation | Format | Methods |
|-----------|--------|---------|
| Logging | .log | write_log(), read_log() |
| Data | JSON | write_json(), read_json() |
| Tabular export | CSV | write_csv(), read_csv() |
| Backup | Binary | backup_database(), restore_database() |

## 8.2 Log Files

### Purpose

System logging provides a persistent record of security events for:
- Debugging
- Audit trail
- Security investigation

### Implementation

```python
def write_log(self, message, log_file="system.log"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def read_log(self, log_file="system.log"):
    try:
        with open(log_file, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        return []
```

**Format:**
```
[2024-01-15 14:30:00] Alert: suspicious_behavior - User 3 night access
[2024-01-15 14:31:00] Suspicious behavior: User 3 - Night access
[2024-01-15 15:00:00] Alert: access_denied - Location not authorized
```

**Log Entry Format:**
- Timestamp: [YYYY-MM-DD HH:MM:SS]
- Message: Event type and description
- Newline terminator

The read method returns empty list if file doesn't exist (no error).

## 8.3 JSON Files

### Purpose

JSON provides structured data interchange for:
- Exporting/importing data
- Configuration files
- API responses

### Implementation

```python
def read_json(self, file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid JSON in file: {file_path}")

def write_json(self, file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
```

**Error Handling:**
- FileNotFoundError: Propagated for missing files
- JSONDecodeError: Wrapped in ValueError for malformed JSON

**Usage in SecurityManager:**

```python
if self.file_manager:
    self.file_manager.write_log(f"Alert: {event_args.alert_type} - {event_args.description}")
```

FileManager is optional (default None) in SecurityManager.

### Export Functions

```python
def export_users_to_json(self, filepath, users):
    data = [user.to_dict() for user in users]
    self.write_json(filepath, data)

def import_users_from_json(self, filepath):
    data = self.read_json(filepath)
    return [User.from_dict(user_data) for user_data in data]

def export_alerts_to_json(self, filepath, alerts):
    data = [alert.to_dict() for alert in alerts]
    self.write_json(filepath, data)
```

## 8.4 CSV Files

### Purpose

CSV provides spreadsheet-compatible format for:
- Spreadsheet analysis
- External system integration

### Implementation

```python
def read_csv(self, file_path):
    try:
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except csv.Error as as e:
        raise ValueError(f"Invalid CSV in file: {file_path}")

def write_csv(self, file_path, data, fieldnames):
    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
```

**Export Example:**

```python
def export_access_logs_to_csv(self, filepath, logs):
    if not logs:
        return
    fieldnames = ['id', 'user_id', 'access_time', 'location', 'status', 'attempts_count']
    data = [log.to_dict() for log in logs]
    self.write_csv(filepath, data, fieldnames)
```

**CSV Format:**
```csv
id,user_id,access_time,location,status,attempts_count
1,1,2024-01-15T09:00:00,IT-101,granted,1
2,1,2024-01-15T14:00:00,FIN-301,denied,1
```

## 8.5 Database Backup and Restore

```python
def backup_database(self, db_manager, backup_path):
    try:
        import shutil
        shutil.copy2(db_manager.db_path, backup_path)
        return True
    except Exception:
        return False

def restore_database(self, db_manager, backup_path):
    try:
        import shutil
        db_manager.close()
        shutil.copy2(backup_path, db_manager.db_path)
        db_manager.connect()
        return True
    except Exception:
        return False
```

Uses shutil.copy2() for file-level copy with metadata preservation.

---

# 9. Event System Analysis

## 9.1 Observer Pattern Implementation

The system implements the Observer pattern using the EventDispatcher class:

```
┌─────────────────────────────────────────────────────────────────────┐
│                  EventDispatcher                      │
├─────────────────────────────────────────────────────┤
│  _listeners: Dict[str, List[callback]]              │
├─────────────────────────────────────────────────────┤
│  + register_listener(event_type, callback)          │
│  + unregister_listener(event_type, callback)       │
│  + dispatch_event(event_type, event_args)            │
│  + get_listeners(event_type)                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 9.2 Event Types

| Event | When Fired | Who Listens |
|-------|-----------|------------|
| on_suspicious_behavior | AI classifies as suspicious | SecurityManager |
| on_access_denied | Access denied | SecurityManager |
| on_multiple_attempts | >3 denials in 60 min | SecurityManager |

## 9.3 Listener Registration

```python
# In app.py
dispatcher.register_listener("on_suspicious_behavior", security_manager.on_suspicious_behavior_handler)
dispatcher.register_listener("on_access_denied", security_manager.on_access_denied_handler)
dispatcher.register_listener("on_multiple_attempts", security_manager.on_multiple_attempts_handler)
```

## 9.4 Event Dispatching

```python
# In AccessController.deny_access()
event_args = AccessEventArgs(user_id, location, reason, timestamp)
self.event_dispatcher.dispatch_event('on_access_denied', event_args)
```

## 9.5 Event Data Structures

Each event type has a dedicated event args class:

### on_suspicious_behavior
```python
class SuspiciousBehaviorEventArgs:
    def __init__(self, user_id, score, reason, timestamp):
        # score: AI confidence (0-1)
        # reason: Human-readable explanation
```

### on_access_denied
```python
class AccessEventArgs:
    def __init__(self, user_id, location, reason, timestamp):
        # location: Requested location
        # reason: Why access was denied
```

### on_multiple_attempts
```python
class AlertEventArgs:
    def __init__(self, user_id, alert_type, description, created_at):
        # alert_type: Type of alert
        # description: Alert details
```

## 9.6 Event Flow Diagrams

### on_suspicious_behavior Flow
```
                         AccessController
                              │
                              ▼
                    analyzer.analyze() returns
                    classification="Suspicious"
                              │
                              ▼
              ┌─────────────────────────────────┐
              │ dispatch_event(                │
              │   'on_suspicious_behavior',    │
              │   SuspiciousBehaviorEventArgs) │
              └─────────────────────────────────┘
                              │
                              ▼
                    EventDispatcher
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          ┌──────────┐ ┌──────────┐ ┌──────────┐
          │Listener1│ │Listener2│ │Listener3│
          │(future) │ │(future) │ │(future) │
          └──────────┘ └──────────┘ └──────────┘
                │             │             │
                ▼             ▼             ▼
         SecurityManager.on_suspicious_behavior_handler
                              │
                              ▼
                    ┌─────────────────┐
                    │ 1. Create Alert│
                    │ 2. Write Log  │
                    └─────────────────┘
```

### on_multiple_attempts Flow
```
                         SecurityManager
                              │
                              ▼
                    monitor_failed_attempts(user_id)
                    5 denials in 60 min
                              │
                              ▼
              ┌─────────────────────────────────┐
              │ dispatch_event(                │
              │   'on_multiple_attempts',     │
              │   AlertEventArgs)           │
              └─────────────────────────────────┘
                              │
                              ▼
                    EventDispatcher ──► SecurityManager handler
                              │
                              ▼
                    ┌─────────────────┐
                    │ Create Alert    │
                    └─────────────────┘
```

---

# 10. LINQ-Style Python Data Analysis

## 10.1 Analysis Module Overview

The src/analysis.py module provides statistical analysis using Python functional programming patterns:

### Patterns Used

- **List comprehensions:** [expr for item in list]
- **map():** Transform items
- **filter():** Select items by condition
- **reduce():** Aggregate items
- **sorted():** Order items
- **defaultdict:** Grouping

## 10.2 Access Pattern Analysis

```python
def analyze_access_patterns(access_logs):
    total = len(access_logs)
    granted = len(list(filter(lambda log: log.status == 'granted', access_logs)))
    denied = len(list(filter(lambda log: log.status == 'denied', access_logs)))
    success_rate = (granted / total * 100) if total > 0 else 0

    by_location = defaultdict(int)
    for log in access_logs:
        by_location[log.location] += 1

    by_day = defaultdict(int)
    for log in access_logs:
        dt = datetime.fromisoformat(log.access_time.replace('Z', '+00:00'))
        by_day[dt.strftime('%A')] += 1
```

**Features:**
- filter() selects by status
- defaultdict groups by location/day
- datetime extracts day names

## 10.3 Peak Access Hours

```python
def get_peak_access_hours(access_logs):
    hour_counts = defaultdict(int)
    for log in access_logs:
        dt = datetime.fromisoformat(log.access_time.replace('Z', '+00:00'))
        hour_counts[dt.hour] += 1

    hour_list = list(map(lambda x: {'hour': x[0], 'count': x[1]}, hour_counts.items()))
    sorted_hours = sorted(hour_list, key=lambda x: x['count'], reverse=True)

    return sorted_hours[:5]
```

**Pattern:**
- map() transforms to dict format
- sorted() orders by count descending
- slice limits to top 5

## 10.4 Anomaly Detection

```python
def detect_anomalies(access_logs):
    # High frequency users
    mean_count = reduce(lambda a, b: a + b, 
                       map(lambda x: x[1], user_counts.items()), 0) / len(user_counts)

    high_frequency_users = list(filter(
        lambda x: x[1] > mean_count * 3,
        user_counts.items()
    ))
```

**Statistics:**
- reduce() calculates mean
- filter() finds >3x mean
- map() extracts counts

## 10.5 Top Users Query

```python
# Using DatabaseManager
def get_most_active_users(self, limit=10):
    cursor.execute('''
        SELECT user_id, COUNT(*) as access_count
        FROM access_logs
        GROUP BY user_id
        ORDER BY access_count DESC
        LIMIT ?
    ''', (limit,))
```

Uses SQL aggregation for efficiency.

---

# 11. Error Handling & Custom Exceptions

## 11.1 Try/Except Usage

### Database Errors

```python
def get_access_frequency(self, user_id, time_window_minutes=60):
    try:
        logs = self.database.get_user_access_logs(user_id)
        # ... process
    except Exception:
        return 0  # Fallback value
```

Returns safe defaults instead of propagating exceptions.

### File Errors

```python
def read_log(self, log_file="system.log"):
    try:
        with open(log_file, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        return []  # Empty list is safe
```

No error - log file not existing is not exceptional.

### Parser Errors

```python
try:
    log_time = datetime.fromisoformat(log.access_time.replace('Z', '+00:00'))
except (ValueError, AttributeError):
    continue  # Skip malformed entries
```

Skips invalid data rather than failing.

## 11.2 Error Responses

APIs return structured errors:

```python
if not user:
    return {
        'granted': False,
        'classification': 'Unknown',
        'confidence_normal': 0,
        'confidence_suspicious': 0,
        'reason': 'User not found'
    }

if 'error' in analysis:
    return fallback_result
```

---

# 12. External Libraries & Dependencies

## 12.1 Libraries Used

| Library | Purpose | Version |
|---------|---------|---------|
| flask | Web framework | Latest |
| scikit-learn | ML classification | Latest |
| sqlite3 | Database | Standard library |
| datetime | DateTime handling | Standard library |
| json | JSON handling | Standard library |
| csv | CSV handling | Standard library |
| pickle | Model serialization | Standard library |
| pytest | Testing | Latest |

## 12.2 scikit-learn Usage

```python
from sklearn.tree import DecisionTreeClassifier

self.model = DecisionTreeClassifier(random_state=42)

# Training
self.model.fit(X, y)

# Prediction
prediction = self.model.predict(feature_array)[0]
proba = self.model.predict_proba(feature_array)[0]
accuracy = self.model.score(X, y)
```

## 12.3 Flask Usage

```python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/endpoint', methods=['GET', 'POST'])
def handler():
    data = request.form or request.json
    return jsonify(response)
```

---

# 13. Security & Access Control Logic

## 13.1 Access Decision Flow

See Section 5.2 for detailed flow.

## 13.2 Security Layers

1. **User validation:** User must exist
2. **Room matching:** Location vs assigned_room
3. **Department matching:** Location prefix vs department
4. **AI Classification:** ML-based detection

## 13.3 Attack Prevention

### Brute Force Prevention
```python
if access_count_last_hour > 3:
    # Flag as suspicious
    # Also dispatch on_multiple_attempts
```

### Night Access Prevention
```python
if hour >= 22 or hour < 6:
    # Flag as suspicious
```

### Unauthorized Location Prevention
```python
if location != assigned_room and not location.startswith(department):
    # Flag as suspicious
```

---

# 14. Detailed Execution Example

## 14.1 Complete Access Request Flow

```python
# User ID 1 requests access to IT-101 at 2024-01-15T14:30:00
result = access_controller.request_access(user_id=1, location="IT-101")
```

### Step-by-Step:

1. **Time:** `access_time = "2024-01-15T14:30:00"`

2. **Database lookup:** User exists with:
   - name: "Alice Johnson"
   - department: "IT"
   - access_level: 3
   - assigned_room: "IT-101"

3. **AI Analysis:** Features extracted:
   - hour: 14
   - minute: 30
   - day_of_week: 0 (Monday)
   - is_weekend: 0
   - access_count_last_hour: 0
   - is_assigned_room: 1 (IT-101 matches)
   - is_same_department: 1 (IT matches)
   - user_access_level: 3
   - historical_denied_count: 0
   - is_night_access: 0

4. **Prediction:** Model classifies as Normal (class 0)

5. **Log created:**
   ```sql
   INSERT INTO access_logs (user_id, access_time, location, status) 
   VALUES (1, '2024-01-15T14:30:00', 'IT-101', 'granted')
   ```

6. **Response:**
   ```python
   {
       'granted': True,
       'classification': 'Normal',
       'confidence_normal': 95.2,
       'confidence_suspicious': 4.8,
       'reason': 'Access pattern appears normal',
       'user_id': 1,
       'location': 'IT-101',
       'timestamp': '2024-01-15T14:30:00'
   }
   ```

### Suspicious Example:

```python
# User 3 requests access to HR-201 at 2024-01-16T03:00:00
result = access_controller.request_access(user_id=3, location="HR-201")
```

Steps:
1. Time: 03:00 (night)
2. User 3 has assigned_room: "FIN-301" (different)
3. Features: is_night=1, is_assigned=0
4. Prediction: Suspicious (class 1)
5. Log created with status='denied'
6. on_suspicious_behavior event dispatched
7. SecurityManager creates Alert
8. Response: granted=False

---

# 15. Design Decisions & Argumentation

## 15.1 Architecture Choices

### Why Flask over CLI/Tkinter?

- **Modern interface:** Web UI is expected for enterprise systems
- **Accessibility:** Works from any device with browser
- **REST API support:** jsonify() enables API integrations
- **Scalability:** Flask can be production-deployed

### Why Events over Direct Calls?

- **Loose coupling:** Publishers don't need to know subscribers
- **Extensibility:** Add listeners without modifying publishers
- **Testability:** Easy to mock event dispatcher

### Why Decision Trees?

- **Interpretability:** Key for school project defense
- **Simplicity:** No hyperparameter tuning needed
- **Requirements:** Meets "rule-based/simple ML" requirement

## 15.2 Database Design

### Why SQLite?

- **No setup:** Zero-configuration database
- **Single file:** Easy to distribute
- **Educational:** SQL concepts are clear
- **Suitable scale:** Correct for single-user application

### Why these tables?

- **users:** Identity and authorization
- **access_logs:** Audit trail
- **alerts:** Security notifications

This is a minimal viable schema for access control.

## 15.3 Event Design

### Why three events?

Per requirements:
- on_suspicious_behavior: AI findings
- on_access_denied: Authorization failures
- on_multiple_attempts: Brute force detection

### Why listener pattern?

Requirements specified "Observer Pattern" and "at least 2 listeners per event".

---

# 16. Project Strengths

## 16.1 Architecture Strengths

1. **Modularity:** Clear separation of concerns
2. **Event-driven:** Loose coupling via events
3. **Dependency injection:** Testable components
4. **Full CRUD:** Complete data operations

## 16.2 Implementation Strengths

1. **Error handling:** Graceful failure handling
2. **Logging:** Multiple logging mechanisms
3. **Serialization:** JSON/CSV export
4. **Testing:** Comprehensive test coverage

## 16.3 AI Integration

1. **Interpretable:** Decision trees are explainable
2. **Multifaceted:** Uses 10 features
3. **Confident:** Provides confidence scores
4. **Reason generation:** Human-readable explanations

---

# 17. Weaknesses & Future Improvements

## 17.1 Current Limitations

1. **No authentication:** Users not authenticated
2. **Static thresholds:** Hardcoded values
3. **Small dataset:** 120 training samples
4. **No user interface for alerts:** Only via events/DB
5. **No dashboard analytics:** Simple statistics only
6. **No real-time alerts:** No notification system

## 17.2 Scalability Concerns

1. **SQLite limitations:** Not suitable for high concurrency
2. **Decision tree overfitting:** Potential with small dataset
3. **No caching:** Repeated AI analysis

## 17.3 Recommendations

1. **Authentication:** Add login system
2. **User interface:** Dashboard with charts
3. **Model improvement:** Random Forest
4. **Data:** Generate larger dataset
5. **Configuration:** External config file

---

# 18. Final Technical Summary

## 18.1 Architecture Summary

The AI Access Control System is a Flask-based web application that combines:

- **Event-driven architecture** via EventDispatcher
- **AI/ML classification** using DecisionTreeClassifier
- **SQLite database** with full CRUD operations
- **File operations** supporting JSON, CSV, and logs

## 18.2 Component Summary

| Component | Responsibility | Lines |
|-----------|----------------|-------|
| BehaviorAnalyzer | AI classification | 242 |
| DatabaseManager | Data persistence | 325 |
| AccessController | Request processing | 132 |
| SecurityManager | Event handling | 104 |
| EventDispatcher | Event system | 22 |
| FileManager | File operations | 89 |
| analysis.py | Statistics | 137 |

## 18.3 Testing Summary

- Unit tests for each component
- Integration tests for workflows
- ~80% coverage target

## 18.4 Documentation Summary

This document provides:

1. Project overview and purpose
2. Detailed folder structure analysis
3. Complete startup sequence documentation
4. Full class documentation for all components
5. Object communication and architecture explanation
6. Complete database schema and CRUD documentation
7. Deep AI/ML system analysis for project defense
8. File handling system documentation
9. Event system analysis
10. LINQ-style analysis patterns
11. Error handling approach
12. External libraries used
13. Security logic explanation
14. Detailed execution examples
15. Design decisions and reasoning
16. Strengths and weaknesses analysis
17. Future improvement recommendations

This documentation should enable developers to understand, maintain, and extend the system while providing sufficient depth for project defense presentations.

---

*Document generated for AI Access Control System Project*
*AI Programming - 11th Grade*