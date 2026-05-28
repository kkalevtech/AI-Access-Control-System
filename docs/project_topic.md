# Project Task: AI Access Control System (Behavior Analysis)

## Project Title

**AI System for Access Control – Behavioral Analysis**

---

## Scenario

The project is a security system that detects suspicious behavior during access attempts. The system analyzes user access patterns and determines whether the behavior is normal or suspicious. Its purpose is to improve security by identifying unusual activity and preventing unauthorized access.

---

# Main Classes

## 1. User

Represents a person who tries to access the system.

Responsibilities:

* user ID
* name
* department
* access level
* assigned room/cabinet

---

## 2. AccessLog

Stores information about every access attempt.

Responsibilities:

* user reference
* date and time
* location
* result (granted / denied)
* number of attempts

---

## 3. BehaviorAnalyzer

The AI component of the system.

Responsibilities:

* analyze access behavior
* classify behavior as:
  * normal
  * suspicious

Analysis is based on:

* access time
* access frequency
* access location

---

## 4. AccessController

Controls access decisions.

Responsibilities:

* process access requests
* allow or deny access
* communicate with the analyzer
* trigger events when needed

---

## 5. SecurityManager

Handles security actions.

Responsibilities:

* receive suspicious behavior alerts
* manage denied access attempts
* monitor repeated failed attempts

---

## 6. EventDispatcher

Implements the Observer Pattern.

Responsibilities:

* event registration
* notifying listeners
* callback execution
* custom event arguments

---

# AI Component

## Classification Task

The system performs a simple classification:

### Output:

* Normal Behavior
* Suspicious Behavior

### Based On:

### 1. Time

Example:

Access at unusual hours such as late night may be suspicious.

### 2. Frequency

Example:

Too many access attempts in a short time may indicate suspicious behavior.

### 3. Location

Example:

Access from an unusual room or department may trigger an alert.

This can be implemented using:

* rule-based AI
* simple ML classification
* basic scoring system

---

# Events

## Required Events

### on_suspicious_behavior

Triggered when suspicious behavior is detected.

Listeners example:

* SecurityManager
* File Logger

---

### on_access_denied

Triggered when access is denied.

Listeners example:

* SecurityManager
* Alert System

---

### on_multiple_attempts

Triggered when too many attempts are detected.

Listeners example:

* SecurityManager
* Database Alert Storage

---

# LINQ-Style Data Analysis Tasks

## 1. Top Users by Access Count

Find users with the highest number of access attempts.

Use:

* sorting
* grouping
* list comprehensions

---

## 2. Unusual Access Hours

Detect access attempts outside normal working hours.

Use:

* filtering
* time analysis

---

## 3. Grouping by Cabinet / Room

Group access logs by location.

Use:

* `groupby()`
* sorting
* reporting

---

# Database Structure

## Table 1: users

Stores system users.

Example fields:

* id
* name
* department
* access_level
* assigned_room

---

## Table 2: access_logs

Stores access attempts.

Example fields:

* id
* user_id
* access_time
* location
* status
* attempts_count

---

## Table 3: alerts

Stores suspicious behavior alerts.

Example fields:

* id
* user_id
* alert_type
* description
* created_at

---

# Project Goal

To build a complete OOP-based Python system that combines:

* security monitoring
* event-driven programming
* database management
* file handling
* behavioral AI analysis

while following all school project requirements for Object-Oriented Programming and AI Programming.
