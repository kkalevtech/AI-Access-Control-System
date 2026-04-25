# AI Agents Working Instructions

This document provides instructions for AI agents working on the AI Access Control System project.

## Project Overview

- **Project Title:** AI System for Access Control – Behavioral Analysis
- **Type:** Python GUI Application with Database and AI/ML Component
- **Target Users:** 11th Grade AI Programming (School Project)

## Required Reading

Before starting any work on this project, ALWAYS read these files first:

1. `@docs\project_requirements.md` - Contains all mandatory OOP requirements
2. `@docs\project_topic.md` - Contains the project topic and class specifications

Both files define what must be implemented and how the system should work.

## Core Requirements

This project must implement the following mandatory elements:

### OOP Structure (Minimum 6 Classes)

- **Data Model Classes:** User, AccessLog
- **AI/ML Logic Class:** BehaviorAnalyzer
- **Controller/Manager Class:** AccessController, SecurityManager
- **Events/Observer Class:** EventDispatcher
- **File Handling Class:** FileHandler
- **Database Handling Class:** DatabaseHandler

### Communication Between Objects

- Objects must interact with each other through method calls
- Implement the Observer Pattern with event-based communication
- Minimum 2 listeners for one event type

### Delegates / Events (Python Style)

- Use callback functions for event handling
- Implement an EventDispatcher class
- Create custom event argument classes

### LINQ-Style Data Processing

Use Python tools for data processing:

- List comprehensions
- `map()`, `filter()`, `reduce()`, `sorted()`, `groupby()`
- Data analysis operations

### File Handling

Support the following file operations:

- Log files (`.log`)
- JSON reading/writing (`.json`)
- CSV reading/writing (`.csv`)

### Exception Handling

- Use `try/except` blocks throughout
- Create custom exception classes
- Handle AI model errors specifically

### Database (SQLite)

- Minimum 3 tables: users, access_logs, alerts
- Full CRUD operations (Create, Read, Update, Delete)

### AI Component

- Rule-based classification or simple ML classification
- Classify behavior as Normal or Suspicious
- Analyze based on: access time, frequency, location

## Working Methods

### Code Style

- Do NOT add comments unless explicitly requested
- Follow existing code conventions in the project
- Use meaningful variable and class names
- Keep code concise and readable

### File Structure

Maintain the following structure:

```
src/
├── models/           # Data model classes
├── ai/               # AI/ML logic
├── controllers/     # Controllers and managers
├── events/          # Event handling
├── database/        # Database handling
├── file_handling/   # File operations
└── ui/              # GUI components
```

### Testing

- Verify functionality after implementation
- Test all CRUD operations
- Test AI classification outputs
- Test event listeners

### Linting and Type Checking

Run lint/typecheck commands if available in the project (check README or package.json).

## Project Events

The system must implement these events with at least 2 listeners each:

1. **on_suspicious_behavior** - Triggered when suspicious behavior detected
   - Listeners: SecurityManager, FileLogger

2. **on_access_denied** - Triggered when access is denied
   - Listeners: SecurityManager, AlertSystem

3. **on_multiple_attempts** - Triggered when too many attempts detected
   - Listeners: SecurityManager, DatabaseAlertStorage

## Database Tables

Design and implement these tables:

1. **users** - id, name, department, access_level, assigned_room
2. **access_logs** - id, user_id, access_time, location, status, attempts_count
3. **alerts** - id, user_id, alert_type, description, created_at

## AI Component Guidelines

The BehaviorAnalyzer should:

- Analyze access patterns (time, frequency, location)
- Classify behavior as Normal or Suspicious
- Use rule-based or simple ML approach
- Be explainable for project defense

Analysis criteria:
- **Time:** Unusual hours (late night) may be suspicious
- **Frequency:** Too many attempts in short time
- **Location:** Access from unusual room/department

## Important Notes

- This is a school project - keep code educational and explainable
- The AI model must be understandable for defense
- Create at least 30 custom records for testing
- Document the development process
- Be prepared for live modifications during defense

## Anti-Requirements

- DO NOT use ready-made AI models without adaptation
- DO NOT copy-paste code without understanding
- All code must be explainable by the student