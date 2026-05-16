# AI Access Control System

An intelligent access control system with AI-powered behavioral analysis for secure access management.

## Features

- **AI-Powered Behavior Analysis**: Machine learning based classification using sklearn DecisionTreeClassifier to detect suspicious access patterns
- **Real-time Monitoring**: Track and monitor user access attempts in real-time
- **Event-driven Architecture**: Observer pattern implementation with event dispatching
- **Web GUI**: Flask-based web interface for system management
- **Database**: SQLite with full CRUD operations
- **File Operations**: JSON, CSV, and log file handling

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Web GUI

```bash
python app.py
```

The database and sample data are generated automatically on first startup.

Then open http://127.0.0.1:5000 in your browser.

### Running Tests

```bash
python -m pytest tests/ -v
```

### Running Tests with Coverage

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

## Project Structure

```
src/
├── ai/                 # AI/ML logic (BehaviorAnalyzer)
├── controllers/        # AccessController, SecurityManager
├── database/          # DatabaseManager
├── events/            # EventDispatcher, EventArgs
├── files/             # FileManager
├── models/            # User, AccessLog, Department, Room
├── analysis.py        # Statistical analysis
└── seed_data.py      # Sample data generation

templates/            # Flask HTML templates
static/css/          # CSS styles
tests/               # Test suite
```

## AI Model

The BehaviorAnalyzer uses a DecisionTreeClassifier trained on:
- Access time (hour, day of week)
- Access frequency
- Room assignment
- Department matching
- Historical denied attempts

## Events

The system implements these events:
- `on_suspicious_behavior` - Triggered when suspicious behavior detected
- `on_access_denied` - Triggered when access is denied
- `on_multiple_attempts` - Triggered when too many failed attempts detected

## Testing

The project includes comprehensive tests:
- Unit tests for all components
- Integration tests for system workflows
- Test coverage: ~80%

## Tech Stack

- Python 3.x
- SQLite
- scikit-learn (ML)
- Flask (Web)
- pandas (Data Analysis)
- pytest (Testing)