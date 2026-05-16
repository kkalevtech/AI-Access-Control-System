# Data Plan — AI Access Control System

## Overview

- **20 users** (each may belong to multiple departments)
- **5 departments**, **30 rooms** (6 per department)
- **400 access logs** (every attempt = separate row, granted or denied)
- **Purpose**: Train a DecisionTreeClassifier on historical access patterns so it can predict **Normal vs Suspicious** behavior for new requests

### Department → Prefix Mapping

| Department   | Prefix |
|-------------|--------|
| Finance     | FIN    |
| HR          | HR     |
| IT          | IT     |
| Marketing   | MKT    |
| Operations  | OPS    |

### Room Codes

Each department has rooms 101, 102, 201, 202, 301, 302:
```
FIN-101, FIN-102, FIN-201, FIN-202, FIN-301, FIN-302
HR-101,  HR-102,  HR-201,  HR-202,  HR-301,  HR-302
IT-101,  IT-102,  IT-201,  IT-202,  IT-301,  IT-302
MKT-101, MKT-102, MKT-201, MKT-202, MKT-301, MKT-302
OPS-101, OPS-102, OPS-201, OPS-202, OPS-301, OPS-302
```

---

## Users & Their Scenarios

### 1. Alice Anderson — Finance Director
- **Departments**: Finance
- **Primary Room**: FIN-201
- **Access Level**: 5
- **Pattern**: Normal office hours (08:00–17:00), weekdays, Finance rooms only
- **ML role**: Establishes the "normal weekday Finance employee" baseline

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | FIN-201  | granted | Normal start of day |
| 10:30:00  | 0       | FIN-202  | granted | Meeting room |
| 11:15:00  | 0       | FIN-101  | granted | Brief visit |
| 14:00:00  | 0       | FIN-301  | granted | Report review |
| 08:15:00  | 0       | FIN-201  | granted | Early start |
| 15:45:00  | 0       | FIN-302  | granted | Filing |
| 12:30:00  | 0       | FIN-201  | granted | Lunch return |
| 16:00:00  | 0       | FIN-102  | granted | End-of-day |
| 09:30:00  | 0       | FIN-201  | granted | Next day |
| 11:00:00  | 0       | FIN-202  | granted | Meeting |
| 13:15:00  | 0       | FIN-301  | granted | Afternoon check |
| 17:30:00  | 0       | FIN-201  | granted | Overtime |
| 08:00:00  | 0       | FIN-101  | granted | Early errand |
| 10:00:00  | 0       | FIN-201  | granted | Daily office |
| 14:30:00  | 0       | FIN-201  | granted | Afternoon work |
| 19:00:00  | 0       | FIN-201  | granted | Evening work |
| 09:00:00  | 0       | HR-101   | denied | Wrong dept |
| 11:00:00  | 0       | IT-101   | denied | Wrong dept |
| 02:30:00  | 0       | FIN-201  | denied | Night — suspicious |
| 23:00:00  | 0       | FIN-201  | denied | Late night — suspicious |

---

### 2. Bob Brown — IT Security Admin
- **Departments**: IT
- **Primary Room**: IT-301 (server room)
- **Access Level**: 5
- **Pattern**: Mostly normal hours, occasional late maintenance; IT rooms only
- **ML role**: Shows that authorized after-hours access still gets granted for trusted users

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 08:30:00  | 0       | IT-301   | granted | Server room check |
| 10:00:00  | 0       | IT-101   | granted | Office work |
| 11:30:00  | 0       | IT-202   | granted | Lab work |
| 14:00:00  | 0       | IT-201   | granted | Dev meeting |
| 15:15:00  | 0       | IT-301   | granted | Server maintenance |
| 09:00:00  | 0       | IT-102   | granted | Shared workspace |
| 13:00:00  | 0       | IT-202   | granted | Lab testing |
| 16:30:00  | 0       | IT-101   | granted | End-of-day tasks |
| 08:00:00  | 0       | IT-301   | granted | Early check |
| 10:30:00  | 0       | IT-201   | granted | Standup |
| 22:00:00  | 0       | IT-301   | granted | Night maintenance (authorized) |
| 23:30:00  | 0       | IT-301   | granted | Late maintenance (authorized) |
| 09:30:00  | 0       | IT-101   | granted | Normal day |
| 14:30:00  | 0       | IT-102   | granted | Collaboration |
| 17:00:00  | 0       | IT-202   | granted | Lab wrap-up |
| 21:00:00  | 0       | IT-301   | granted | Evening patch |
| 03:00:00  | 0       | FIN-101  | denied | Wrong dept, night — suspicious |
| 10:00:00  | 0       | HR-201   | denied | Unauthorized dept |
| 08:30:00  | 1       | IT-301   | granted | Weekend maintenance |
| 11:00:00  | 1       | IT-101   | granted | Weekend work |

---

### 3. Carol Chen — HR Manager
- **Departments**: HR
- **Primary Room**: HR-201
- **Access Level**: 4
- **Pattern**: Strictly business hours (09:00–17:00), weekdays, HR rooms only
- **ML role**: Clean pattern — easy for model to learn as "normal"

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | HR-201   | granted | Morning start |
| 10:15:00  | 0       | HR-101   | granted | Employee meeting |
| 11:30:00  | 0       | HR-102   | granted | File room |
| 14:00:00  | 0       | HR-301   | granted | Director meeting |
| 15:30:00  | 0       | HR-201   | granted | Desk work |
| 09:15:00  | 0       | HR-201   | granted | Next day |
| 10:00:00  | 0       | HR-301   | granted | Strategy meeting |
| 13:00:00  | 0       | HR-102   | granted | Records |
| 16:00:00  | 0       | HR-201   | granted | Wrap-up |
| 09:30:00  | 0       | HR-101   | granted | Interview |
| 11:00:00  | 0       | HR-201   | granted | Paperwork |
| 14:30:00  | 0       | HR-202   | granted | Training room |
| 17:00:00  | 0       | HR-201   | granted | Overtime |
| 08:45:00  | 0       | HR-101   | granted | Early |
| 12:00:00  | 0       | HR-201   | granted | Lunch return |
| 15:00:00  | 0       | HR-301   | granted | Afternoon meeting |
| 09:00:00  | 0       | IT-101   | denied | Unauthorized dept |
| 14:00:00  | 0       | FIN-201  | denied | Unauthorized dept |
| 22:00:00  | 0       | HR-201   | denied | Night — suspicious |
| 10:00:00  | 1       | HR-201   | denied | Weekend — not her pattern |

---

### 4. David Davis — Night Security Guard
- **Departments**: Operations
- **Primary Room**: OPS-101 (security office)
- **Access Level**: 3
- **Pattern**: Night shift (20:00–06:00), patrols all departments, works weekends
- **ML role**: Establishes "night access is normal for THIS user" so the ML doesn't flag all night access

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 20:00:00  | 0       | OPS-101  | granted | Shift start |
| 21:30:00  | 0       | FIN-101  | granted | Patrol |
| 22:45:00  | 0       | IT-301   | granted | Patrol |
| 00:15:00  | 0       | HR-101   | granted | Patrol |
| 02:00:00  | 0       | MKT-201  | granted | Patrol |
| 04:30:00  | 0       | OPS-101  | granted | Break |
| 05:45:00  | 0       | OPS-202  | granted | End-of-shift report |
| 20:30:00  | 0       | OPS-101  | granted | Next shift |
| 23:00:00  | 0       | FIN-302  | granted | Patrol |
| 01:30:00  | 0       | OPS-102  | granted | Patrol |
| 03:15:00  | 0       | IT-101   | granted | Patrol |
| 06:00:00  | 0       | OPS-101  | granted | Shift end |
| 21:00:00  | 1       | OPS-101  | granted | Weekend shift |
| 23:30:00  | 1       | MKT-101  | granted | Weekend patrol |
| 02:00:00  | 1       | HR-201   | granted | Weekend patrol |
| 05:00:00  | 1       | OPS-101  | granted | Weekend end |
| 20:00:00  | 0       | OPS-101  | granted | Another shift |
| 22:00:00  | 0       | FIN-101  | granted | Patrol |
| 00:30:00  | 0       | IT-202   | granted | Patrol |
| 04:00:00  | 0       | OPS-301  | granted | Final patrol |

---

### 5. Eve Edwards — Marketing Lead
- **Departments**: Marketing
- **Primary Room**: MKT-201
- **Access Level**: 4
- **Pattern**: Normal hours with occasional evening campaign work; Marketing rooms
- **ML role**: Occasional after-hours but still authorized

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | MKT-201  | granted | Morning start |
| 10:30:00  | 0       | MKT-101  | granted | Team meeting |
| 11:45:00  | 0       | MKT-202  | granted | Creative session |
| 14:00:00  | 0       | MKT-301  | granted | Campaign planning |
| 15:30:00  | 0       | MKT-201  | granted | Desk work |
| 09:15:00  | 0       | MKT-201  | granted | Next day |
| 10:00:00  | 0       | MKT-301  | granted | Strategy |
| 13:00:00  | 0       | MKT-102  | granted | Content review |
| 16:00:00  | 0       | MKT-201  | granted | Wrap-up |
| 20:00:00  | 0       | MKT-201  | granted | Evening campaign work |
| 21:30:00  | 0       | MKT-202  | granted | Late creative session |
| 09:30:00  | 0       | MKT-101  | granted | Standup |
| 14:00:00  | 0       | MKT-201  | granted | Afternoon work |
| 11:00:00  | 0       | FIN-101  | denied | Wrong dept |
| 15:00:00  | 0       | IT-201   | denied | Wrong dept |
| 03:00:00  | 0       | MKT-201  | denied | Night — suspicious |
| 10:00:00  | 1       | MKT-201  | granted | Weekend campaign push |
| 14:00:00  | 1       | MKT-101  | granted | Weekend work |
| 08:30:00  | 0       | MKT-201  | granted | Normal morning |
| 17:00:00  | 0       | MKT-201  | granted | Regular end |

---

### 6. Frank Foster — Finance Intern
- **Departments**: Finance
- **Primary Room**: (none — shared cubicle area)
- **Access Level**: 1 (lowest)
- **Pattern**: Normal hours, many denials (low access level trying restricted rooms)
- **ML role**: Shows low-level user with frequent denials — model should learn denials correlate with low level

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | FIN-101  | granted | Shared cubicle (allowed) |
| 10:00:00  | 0       | FIN-102  | granted | Filing (allowed) |
| 11:00:00  | 0       | FIN-101  | granted | Desk work |
| 14:00:00  | 0       | FIN-102  | granted | Errand |
| 09:30:00  | 0       | FIN-101  | granted | Next day |
| 10:30:00  | 0       | FIN-202  | denied | Meeting room — restricted |
| 11:00:00  | 0       | FIN-301  | denied | Supervisors only |
| 15:00:00  | 0       | FIN-201  | denied | Director's office |
| 09:00:00  | 0       | FIN-101  | granted | Desk work |
| 10:00:00  | 0       | FIN-302  | denied | Restricted room |
| 14:00:00  | 0       | HR-101   | denied | Wrong dept |
| 15:30:00  | 0       | FIN-101  | granted | End of day |
| 08:45:00  | 0       | FIN-101  | granted | Early start |
| 11:30:00  | 0       | FIN-102  | granted | Filing |
| 13:00:00  | 0       | FIN-201  | denied | Director office (still restricted) |
| 16:00:00  | 0       | FIN-101  | granted | Wrap-up |
| 22:00:00  | 0       | FIN-101  | denied | Night — suspicious |
| 10:00:00  | 1       | FIN-101  | denied | Weekend — not his pattern |
| 09:00:00  | 0       | FIN-101  | granted | Normal day |
| 12:00:00  | 0       | FIN-102  | granted | Lunch area |

---

### 7. Grace Garcia — Operations Supervisor
- **Departments**: Operations
- **Primary Room**: OPS-202
- **Access Level**: 3
- **Pattern**: Standard office hours, Operations rooms only
- **ML role**: Clean normal pattern

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 08:30:00  | 0       | OPS-202  | granted | Morning start |
| 09:45:00  | 0       | OPS-101  | granted | Check-in |
| 11:00:00  | 0       | OPS-201  | granted | Meeting |
| 13:00:00  | 0       | OPS-202  | granted | Desk work |
| 14:30:00  | 0       | OPS-301  | granted | Inventory |
| 08:00:00  | 0       | OPS-202  | granted | Early |
| 10:00:00  | 0       | OPS-102  | granted | Walkthrough |
| 13:30:00  | 0       | OPS-201  | granted | Planning |
| 15:00:00  | 0       | OPS-202  | granted | Reports |
| 16:30:00  | 0       | OPS-101  | granted | End-of-day |
| 09:00:00  | 0       | OPS-202  | granted | Next day |
| 11:30:00  | 0       | OPS-301  | granted | Inventory check |
| 14:00:00  | 0       | OPS-201  | granted | Staff meeting |
| 08:30:00  | 0       | OPS-202  | granted | Normal day |
| 12:00:00  | 0       | OPS-102  | granted | Walkthrough |
| 15:30:00  | 0       | OPS-202  | granted | End-of-day |
| 10:00:00  | 0       | FIN-101  | denied | Wrong dept |
| 14:00:00  | 0       | IT-101   | denied | Wrong dept |
| 23:00:00  | 0       | OPS-202  | denied | Night — suspicious |
| 09:00:00  | 1       | OPS-101  | denied | Weekend — unusual |

---

### 8. Henry Harris — Ex-Employee (credentials not yet revoked)
- **Departments**: IT (was in IT, now deactivated access_level=1)
- **Primary Room**: IT-101 (was his old office)
- **Access Level**: 1 (effectively deactivated)
- **Pattern**: Tries old room at odd hours, frequently denied
- **ML role**: Models ex-employee or compromised account behavior — high denial rate, odd hours

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | IT-101   | granted | Old office — still sometimes let in |
| 10:30:00  | 0       | IT-201   | denied | No longer authorized |
| 11:00:00  | 0       | IT-102   | denied | No access |
| 14:00:00  | 0       | IT-101   | granted | Still has some access |
| 15:30:00  | 0       | IT-301   | denied | Server room — blocked |
| 22:00:00  | 0       | IT-101   | denied | Night — suspicious |
| 23:30:00  | 0       | IT-201   | denied | Late night — suspicious |
| 02:00:00  | 0       | IT-101   | denied | Very late — suspicious |
| 03:30:00  | 0       | FIN-101  | denied | Wrong dept, night |
| 10:00:00  | 0       | IT-101   | granted | Sometimes granted (inconsistency) |
| 11:30:00  | 0       | HR-101   | denied | Unauthorized |
| 13:00:00  | 0       | IT-101   | granted | Midday — sometimes works |
| 21:00:00  | 0       | IT-202   | denied | Night, unauthorized |
| 01:00:00  | 0       | OPS-101  | denied | Night, wrong dept |
| 12:00:00  | 0       | IT-101   | granted | Sometimes works |
| 16:00:00  | 0       | IT-101   | granted | Late afternoon |
| 20:00:00  | 0       | IT-301   | denied | Night, restricted |
| 00:30:00  | 0       | IT-101   | denied | Midnight — suspicious |
| 09:30:00  | 0       | IT-101   | granted | Normal time — sometimes works |
| 17:00:00  | 0       | IT-101   | granted | End of day |

---

### 9. Iris Huang — Cross-Department Coordinator
- **Departments**: Finance, HR, Operations
- **Primary Room**: FIN-301
- **Access Level**: 3
- **Pattern**: Normal hours, accesses all three of her departments freely
- **ML role**: Shows multi-department authorized access — model learns she's normal in multiple depts

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 08:30:00  | 0       | FIN-301  | granted | Her office |
| 09:45:00  | 0       | HR-101   | granted | HR coordination |
| 11:00:00  | 0       | OPS-201  | granted | Ops meeting |
| 13:00:00  | 0       | FIN-301  | granted | Desk work |
| 14:30:00  | 0       | HR-201   | granted | HR strategy |
| 09:00:00  | 0       | OPS-101  | granted | Ops check |
| 10:30:00  | 0       | FIN-102  | granted | Finance errand |
| 13:30:00  | 0       | HR-102   | granted | Records |
| 15:00:00  | 0       | OPS-202  | granted | Ops planning |
| 08:00:00  | 0       | FIN-301  | granted | Early start |
| 10:00:00  | 0       | OPS-301  | granted | Inventory coordination |
| 11:30:00  | 0       | HR-301   | granted | HR directors |
| 14:00:00  | 0       | FIN-201  | granted | Finance meeting |
| 16:00:00  | 0       | FIN-301  | granted | End-of-day |
| 09:30:00  | 0       | HR-201   | granted | HR sync |
| 11:00:00  | 0       | OPS-201  | granted | Ops standup |
| 15:30:00  | 0       | IT-101   | denied | Not her dept |
| 22:00:00  | 0       | FIN-301  | denied | Night — suspicious |
| 10:00:00  | 1       | FIN-301  | denied | Weekend — not her pattern |
| 14:00:00  | 0       | MKT-101  | denied | Not her dept |

---

### 10. Jack Johnson — Suspicious Outsider
- **Departments**: (none)
- **Primary Room**: none
- **Access Level**: 1
- **Pattern**: Random access attempts to various rooms at various hours, mostly denied
- **ML role**: Models truly suspicious behavior — high denial rate, no pattern

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | FIN-101  | denied | Random attempt |
| 10:30:00  | 0       | IT-301   | denied | Random attempt |
| 12:00:00  | 0       | HR-201   | denied | Random attempt |
| 14:00:00  | 0       | FIN-201  | denied | Random attempt |
| 15:30:00  | 0       | MKT-101  | denied | Random attempt |
| 22:00:00  | 0       | OPS-101  | denied | Night random |
| 23:00:00  | 0       | IT-101   | denied | Night random |
| 01:00:00  | 0       | HR-102   | denied | Late night |
| 03:00:00  | 0       | FIN-302  | denied | Very late |
| 11:00:00  | 0       | OPS-301  | denied | Random |
| 13:00:00  | 0       | MKT-201  | denied | Random |
| 16:00:00  | 0       | IT-202   | denied | Random |
| 08:00:00  | 0       | HR-301   | denied | Random |
| 20:00:00  | 0       | FIN-101  | denied | Evening random |
| 02:30:00  | 0       | MKT-301  | denied | Late night |
| 10:00:00  | 0       | OPS-102  | denied | Random |
| 14:30:00  | 0       | IT-102   | denied | Random |
| 17:00:00  | 0       | HR-101   | denied | Random |
| 21:00:00  | 0       | FIN-201  | denied | Night random |
| 05:00:00  | 0       | OPS-202  | denied | Early morning random |

---

### 11. Karen Kim — Executive Assistant
- **Departments**: Finance, IT, Marketing, HR, Operations (all)
- **Primary Room**: FIN-101 (EA office near CEO)
- **Access Level**: 4
- **Pattern**: Normal hours, accesses all departments for executive support
- **ML role**: Shows "high-trust user with access everywhere" — almost always granted

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 08:00:00  | 0       | FIN-101  | granted | Office |
| 09:15:00  | 0       | HR-201   | granted | Schedule meeting |
| 10:30:00  | 0       | IT-101   | granted | Tech support coordination |
| 11:45:00  | 0       | MKT-201  | granted | Marketing sync |
| 13:00:00  | 0       | OPS-202  | granted | Ops coordination |
| 08:30:00  | 0       | FIN-101  | granted | Desk |
| 09:00:00  | 0       | FIN-201  | granted | Finance errand |
| 10:00:00  | 0       | HR-101   | granted | HR errand |
| 14:00:00  | 0       | IT-201   | granted | IT coordination |
| 15:30:00  | 0       | MKT-101  | granted | Marketing errand |
| 08:00:00  | 0       | FIN-101  | granted | Morning |
| 10:00:00  | 0       | OPS-101  | granted | Ops errand |
| 11:00:00  | 0       | HR-301   | granted | HR directors |
| 13:30:00  | 0       | MKT-301  | granted | Marketing planning |
| 15:00:00  | 0       | IT-301   | granted | Server room (with CEO) |
| 16:30:00  | 0       | FIN-101  | granted | End-of-day |
| 09:00:00  | 0       | OPS-301  | granted | Ops inventory |
| 11:30:00  | 0       | FIN-102  | granted | Filing |
| 14:30:00  | 0       | HR-102   | granted | Records |
| 17:00:00  | 0       | FIN-101  | granted | Wrap-up |

---

### 12. Leo Lopez — Cleaner / Maintenance
- **Departments**: Operations
- **Primary Room**: OPS-302 (storage)
- **Access Level**: 2
- **Pattern**: Early mornings (05:00–07:00) and evenings (19:00–22:00), accesses ALL rooms
- **ML role**: Shows that unusual-hour + all-rooms still = normal for certain roles

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 05:30:00  | 0       | FIN-101  | granted | Morning cleaning |
| 06:15:00  | 0       | IT-201   | granted | IT cleaning |
| 06:45:00  | 0       | HR-101   | granted | HR cleaning |
| 19:30:00  | 0       | MKT-201  | granted | Evening cleaning |
| 20:15:00  | 0       | OPS-101  | granted | Ops cleaning |
| 21:00:00  | 0       | FIN-301  | granted | Evening finance |
| 05:00:00  | 0       | OPS-302  | granted | Storage access |
| 06:00:00  | 0       | HR-201   | granted | HR cleaning |
| 20:00:00  | 0       | IT-101   | granted | IT evening clean |
| 21:30:00  | 0       | MKT-101  | granted | Marketing clean |
| 05:30:00  | 1       | FIN-101  | granted | Weekend cleaning |
| 06:30:00  | 1       | IT-301   | granted | Weekend clean |
| 20:00:00  | 1       | OPS-201  | granted | Weekend evening |
| 21:00:00  | 1       | HR-102   | granted | Weekend clean |
| 05:45:00  | 0       | MKT-301  | granted | Morning marketing |
| 19:00:00  | 0       | FIN-102  | granted | Evening finance |
| 20:30:00  | 0       | OPS-202  | granted | Evening ops |
| 22:00:00  | 0       | OPS-302  | granted | Storage return |
| 06:00:00  | 0       | IT-202   | granted | Morning IT lab |
| 21:00:00  | 0       | HR-301   | granted | Evening HR |

---

### 13. Maria Martinez — Senior Developer
- **Departments**: IT
- **Primary Room**: IT-202 (lab)
- **Access Level**: 4
- **Pattern**: Normal + crunch-time late hours; IT rooms only
- **ML role**: Mix of normal and late hours — model learns late hours in familiar rooms are OK

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | IT-202   | granted | Lab work |
| 10:30:00  | 0       | IT-101   | granted | Team standup |
| 11:45:00  | 0       | IT-201   | granted | Code review |
| 14:00:00  | 0       | IT-102   | granted | Collaboration |
| 15:30:00  | 0       | IT-202   | granted | Deep work |
| 09:15:00  | 0       | IT-202   | granted | Next day |
| 11:00:00  | 0       | IT-301   | granted | Server check |
| 13:00:00  | 0       | IT-101   | granted | Lunch |
| 16:00:00  | 0       | IT-201   | granted | Code review |
| 22:00:00  | 0       | IT-202   | granted | Crunch time |
| 23:00:00  | 0       | IT-202   | granted | Late crunch |
| 01:00:00  | 0       | IT-101   | granted | Very late (authorized) |
| 09:00:00  | 0       | IT-202   | granted | Normal day |
| 14:30:00  | 0       | IT-202   | granted | Afternoon lab |
| 10:00:00  | 1       | IT-202   | granted | Weekend crunch |
| 14:00:00  | 1       | IT-101   | granted | Weekend work |
| 10:00:00  | 0       | FIN-101  | denied | Wrong dept |
| 15:00:00  | 0       | HR-201   | denied | Wrong dept |
| 03:00:00  | 0       | MKT-101  | denied | Night — wrong dept |
| 08:30:00  | 0       | IT-202   | granted | Early lab |

---

### 14. Nathan Nguyen — New Marketing Hire
- **Departments**: Marketing
- **Primary Room**: MKT-101 (shared cubicle)
- **Access Level**: 1
- **Pattern**: Normal hours, still learning — some unauthorized attempts, many denials
- **ML role**: Shows new employee with low access and exploration attempts

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | MKT-101  | granted | Cubicle |
| 10:00:00  | 0       | MKT-102  | granted | Shared area |
| 11:00:00  | 0       | MKT-201  | denied | Lead's office — restricted |
| 14:00:00  | 0       | MKT-101  | granted | Desk work |
| 15:00:00  | 0       | MKT-301  | denied | Campaign room — restricted |
| 09:30:00  | 0       | MKT-101  | granted | Next day |
| 10:30:00  | 0       | MKT-102  | granted | Content review |
| 11:00:00  | 0       | MKT-202  | denied | Creative room — restricted |
| 13:00:00  | 0       | MKT-101  | granted | Desk work |
| 14:30:00  | 0       | FIN-101  | denied | Wrong dept |
| 16:00:00  | 0       | MKT-101  | granted | End of day |
| 09:00:00  | 0       | MKT-101  | granted | Desk |
| 10:00:00  | 0       | IT-101   | denied | Wrong dept |
| 11:30:00  | 0       | MKT-102  | granted | Shared area |
| 14:00:00  | 0       | MKT-101  | granted | Work |
| 15:00:00  | 0       | HR-101   | denied | Wrong dept |
| 08:30:00  | 0       | MKT-101  | granted | Early start |
| 12:00:00  | 0       | MKT-102  | granted | Lunch area |
| 22:00:00  | 0       | MKT-101  | denied | Night — suspicious |
| 10:00:00  | 1       | MKT-101  | denied | Weekend — unusual |

---

### 15. Olivia Owens — CEO
- **Departments**: Finance, IT, Marketing, HR, Operations (all)
- **Primary Room**: FIN-101 (executive office)
- **Access Level**: 5 (highest)
- **Pattern**: Any hours, any room — always granted
- **ML role**: Shows top-level executive with universal access

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 07:30:00  | 0       | FIN-101  | granted | Early start |
| 09:00:00  | 0       | HR-201   | granted | HR meeting |
| 10:00:00  | 0       | IT-301   | granted | Server tour |
| 11:30:00  | 0       | MKT-201  | granted | Marketing review |
| 13:00:00  | 0       | OPS-202  | granted | Ops lunch meeting |
| 14:00:00  | 0       | FIN-201  | granted | Finance strategy |
| 15:30:00  | 0       | IT-101   | granted | IT visit |
| 08:00:00  | 0       | FIN-101  | granted | Morning office |
| 09:00:00  | 1       | FIN-101  | granted | Weekend work |
| 10:00:00  | 1       | OPS-101  | granted | Weekend visit |
| 22:00:00  | 0       | FIN-101  | granted | Late night work |
| 23:00:00  | 0       | IT-202   | granted | Late IT visit |
| 08:30:00  | 0       | FIN-101  | granted | Regular start |
| 10:00:00  | 0       | MKT-301  | granted | Campaign review |
| 13:30:00  | 0       | HR-101   | granted | HR check |
| 15:00:00  | 0       | OPS-301  | granted | Inventory tour |
| 09:00:00  | 0       | IT-102   | granted | IT walkthrough |
| 11:00:00  | 0       | FIN-302  | granted | Finance visit |
| 14:00:00  | 0       | MKT-101  | granted | Marketing check |
| 17:00:00  | 0       | FIN-101  | granted | End of day |

---

### 16. Paul Patel — Part-Time Consultant
- **Departments**: IT, Marketing
- **Primary Room**: IT-102 (shared workspace)
- **Access Level**: 2
- **Pattern**: Afternoons only (12:00–17:00), his two departments
- **ML role**: Limited-hour access — model should learn he shouldn't appear in mornings

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 12:00:00  | 0       | IT-102   | granted | Start of day |
| 13:00:00  | 0       | IT-101   | granted | IT work |
| 14:30:00  | 0       | MKT-201  | granted | Marketing consulting |
| 15:45:00  | 0       | IT-102   | granted | Wrap-up |
| 12:30:00  | 0       | MKT-101  | granted | Marketing desk |
| 14:00:00  | 0       | IT-201   | granted | IT meeting |
| 16:00:00  | 0       | MKT-102  | granted | Final check |
| 12:00:00  | 0       | IT-102   | granted | Start |
| 13:30:00  | 0       | MKT-301  | granted | Campaign input |
| 15:00:00  | 0       | IT-101   | granted | IT work |
| 16:30:00  | 0       | MKT-201  | granted | Marketing sync |
| 12:15:00  | 0       | IT-102   | granted | Start |
| 13:00:00  | 0       | IT-202   | granted | Lab visit |
| 14:30:00  | 0       | MKT-101  | granted | Marketing |
| 16:00:00  | 0       | IT-102   | granted | End |
| 08:00:00  | 0       | IT-102   | denied | Morning — not his hours (suspicious) |
| 10:00:00  | 0       | OPS-101  | denied | Wrong dept |
| 22:00:00  | 0       | IT-102   | denied | Night — not his pattern |
| 12:00:00  | 1       | IT-102   | denied | Weekend — not his pattern |
| 09:00:00  | 0       | FIN-101  | denied | Morning + wrong dept |

---

### 17. Quinn Chen — Weekend IT Support
- **Departments**: IT
- **Primary Room**: IT-101
- **Access Level**: 3
- **Pattern**: Works only on weekends, IT rooms
- **ML role**: Shows weekend-only pattern — model learns weekend ≠ suspicious for this user

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 1       | IT-101   | granted | Weekend support |
| 10:30:00  | 1       | IT-201   | granted | Weekend maintenance |
| 12:00:00  | 1       | IT-102   | granted | Shared workspace |
| 14:00:00  | 1       | IT-301   | granted | Server check |
| 15:30:00  | 1       | IT-101   | granted | Wrap-up |
| 09:00:00  | 1       | IT-101   | granted | Next weekend |
| 11:00:00  | 1       | IT-202   | granted | Lab check |
| 13:00:00  | 1       | IT-101   | granted | Desk |
| 15:00:00  | 1       | IT-301   | granted | Server |
| 08:30:00  | 1       | IT-101   | granted | Early weekend |
| 10:00:00  | 1       | IT-102   | granted | Workspace |
| 12:30:00  | 1       | IT-201   | granted | Maintenance |
| 14:30:00  | 1       | IT-301   | granted | Server |
| 16:00:00  | 1       | IT-101   | granted | End |
| 09:00:00  | 1       | IT-101   | granted | Weekend |
| 10:00:00  | 0       | IT-101   | denied | Weekday — never works weekdays |
| 14:00:00  | 0       | IT-101   | denied | Weekday — suspicious |
| 09:00:00  | 1       | FIN-101  | granted | Weekend errand (allowed) |
| 11:00:00  | 1       | HR-201   | denied | Wrong dept |
| 22:00:00  | 1       | IT-101   | denied | Weekend night — suspicious |

---

### 18. Rachel Robinson — Night Finance Auditor
- **Departments**: Finance
- **Primary Room**: FIN-102 (audit room)
- **Access Level**: 3
- **Pattern**: Night hours (22:00–02:00), Finance rooms only, weekdays
- **ML role**: Shows authorized night access for specific role — night ≠ always suspicious

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 22:00:00  | 0       | FIN-102  | granted | Audit start |
| 23:15:00  | 0       | FIN-101  | granted | Records check |
| 00:30:00  | 0       | FIN-301  | granted | Report room |
| 01:45:00  | 0       | FIN-102  | granted | Audit end |
| 22:30:00  | 0       | FIN-102  | granted | Next audit |
| 23:00:00  | 0       | FIN-201  | granted | File access |
| 00:00:00  | 0       | FIN-302  | granted | Storage |
| 01:00:00  | 0       | FIN-102  | granted | Wrap-up |
| 22:00:00  | 0       | FIN-102  | granted | Audit |
| 23:30:00  | 0       | FIN-101  | granted | Records |
| 00:15:00  | 0       | FIN-201  | granted | Files |
| 01:30:00  | 0       | FIN-102  | granted | End |
| 22:00:00  | 0       | FIN-102  | granted | Audit |
| 23:45:00  | 0       | FIN-301  | granted | Reports |
| 01:00:00  | 0       | FIN-102  | granted | Close |
| 22:30:00  | 0       | FIN-102  | granted | Audit |
| 09:00:00  | 0       | FIN-102  | denied | Morning — not her hours |
| 22:00:00  | 0       | IT-101   | denied | Wrong dept |
| 23:00:00  | 0       | MKT-101  | denied | Wrong dept |
| 22:00:00  | 1       | FIN-102  | denied | Weekend — not her pattern |

---

### 19. Sam Stevens — Brute Force Attacker (simulated)
- **Departments**: (none)
- **Primary Room**: none
- **Access Level**: 1
- **Pattern**: Rapid multiple attempts to different rooms in very short time windows, all denied
- **ML role**: Tests frequency-based detection — many attempts in the same hour

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 02:00:00  | 0       | FIN-101  | denied | Burst attack |
| 02:01:00  | 0       | FIN-102  | denied | Burst attack |
| 02:03:00  | 0       | FIN-201  | denied | Burst attack |
| 02:04:00  | 0       | IT-101   | denied | Burst attack |
| 02:06:00  | 0       | HR-101   | denied | Burst attack |
| 02:07:00  | 0       | MKT-101  | denied | Burst attack |
| 02:09:00  | 0       | OPS-101  | denied | Burst attack |
| 02:10:00  | 0       | FIN-301  | denied | Burst attack |
| 02:12:00  | 0       | IT-301   | denied | Burst attack |
| 02:13:00  | 0       | HR-201   | denied | Burst attack |
| 14:00:00  | 0       | FIN-101  | denied | Slow attempt |
| 14:05:00  | 0       | IT-101   | denied | Slow attempt |
| 14:10:00  | 0       | HR-101   | denied | Slow attempt |
| 14:15:00  | 0       | MKT-101  | denied | Slow attempt |
| 03:00:00  | 0       | FIN-101  | denied | Another burst |
| 03:01:00  | 0       | FIN-102  | denied | Burst |
| 03:02:00  | 0       | FIN-201  | denied | Burst |
| 03:03:00  | 0       | IT-101   | denied | Burst |
| 03:05:00  | 0       | HR-101   | denied | Burst |
| 03:06:00  | 0       | MKT-101  | denied | Burst |

---

### 20. Tina Turner — Department Hopper
- **Departments**: Marketing
- **Primary Room**: MKT-301
- **Access Level**: 2
- **Pattern**: Normal hours, tries every department, mixed results — some granted, some denied
- **ML role**: Tests location-based pattern analysis — model sees mixed grant/deny pattern

| Time       | Weekend | Location | Status | Why |
|-----------|---------|----------|--------|-----|
| 09:00:00  | 0       | MKT-301  | granted | Her office |
| 10:00:00  | 0       | FIN-101  | denied | Hopping — wrong dept |
| 11:00:00  | 0       | MKT-201  | granted | Marketing room |
| 13:00:00  | 0       | IT-101   | denied | Hopping — wrong dept |
| 14:00:00  | 0       | MKT-102  | granted | Marketing room |
| 09:30:00  | 0       | MKT-301  | granted | Her office |
| 10:30:00  | 0       | HR-101   | denied | Hopping |
| 11:30:00  | 0       | MKT-101  | granted | Marketing |
| 14:00:00  | 0       | OPS-101  | denied | Hopping |
| 15:00:00  | 0       | MKT-201  | granted | Marketing |
| 09:00:00  | 0       | MKT-301  | granted | Office |
| 10:00:00  | 0       | IT-201   | denied | Hopping |
| 11:00:00  | 0       | MKT-301  | granted | Office |
| 14:00:00  | 0       | HR-201   | denied | Hopping |
| 15:30:00  | 0       | MKT-102  | granted | Marketing |
| 08:30:00  | 0       | MKT-301  | granted | Office |
| 10:00:00  | 0       | FIN-201  | denied | Hopping |
| 11:00:00  | 0       | MKT-301  | granted | Office |
| 22:00:00  | 0       | MKT-301  | denied | Night — suspicious |
| 10:00:00  | 1       | MKT-301  | denied | Weekend — unusual |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total users | 20 |
| Departments | 5 |
| Rooms | 30 |
| Total access logs | 400 |
| Weekend logs | ~60 (15%) |
| Weekday logs | ~340 (85%) |
| Granted | ~280 (70%) |
| Denied | ~120 (30%) |

### Users by department count
- 1 department: Alice, Bob, Carol, David, Eve, Frank, Grace, Henry, Maria, Nathan, Quinn, Rachel, Tina (13 users)
- 2 departments: Paul (1 user)
- 3 departments: Iris (1 user)
- 5 departments (all): Karen, Olivia (2 users)
- 0 departments: Jack, Sam (2 users)

---

## ML Training Strategy

The DecisionTreeClassifier is trained on all 400 logs. Features extracted per log:

- `hour`, `minute` — time of day
- `day_of_week` — derived from is_weekend (0=weekday, 6=weekend)
- `is_weekend` — 0 or 1
- `access_count_last_hour` — frequency feature (important for Sam's bursts)
- `is_assigned_room` — is this the user's primary room?
- `is_same_department` — does user belong to the accessed room's department?
- `user_access_level` — 1-5
- `historical_denied_count` — total denials for this user
- `is_night_access` — hour >= 22 or hour < 6
- `user_location_grant_rate` — historical grant rate for this user+location pair (KEY feature)

**Labeling rule**: A log is labeled "suspicious" if:
1. Historical grant rate for this user+location ≤ 0.3, OR
2. Night access AND grant rate < 0.5, OR  
3. More than 3 attempts in the last hour, OR
4. No history (grant rate = 0.5) AND not assigned room

After training, the model learns which feature combinations predict suspicious vs normal behavior. When a new request comes in, it extracts the same features and predicts a class with confidence scores.

### What the ML should learn

| Scenario | Expected Prediction |
|---------|-------------------|
| Alice accessing FIN-201 at 09:00 (normal pattern) | Normal (confident) |
| David accessing OPS-101 at 22:00 (night guard) | Normal (from high grant rate) |
| Sam's rapid burst at 02:00 | Suspicious (high frequency) |
| Jack's random access | Suspicious (low grant rate, no pattern) |
| Olivia accessing anywhere at any time | Normal (always granted historically) |
| Henry trying IT-301 at night | Suspicious (low grant rate, night) |
| Quinn accessing IT on weekend | Normal (all his history is weekend) |
| Paul trying IT at 08:00 (morning, not his hours) | Suspicious (no history at that time) |
