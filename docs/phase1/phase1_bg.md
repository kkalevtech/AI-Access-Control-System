# Фаза 1: Анализ и дизайн

**Този документ е предварителен план и подлежи на промени по време на изпълнение.**

## 1. Идея на проекта (разбираем език)

Този проект е AI базирана система за сигурност, която наблюдава и анализира опитите за достъп на потребителите до сграда или помещение. Системата следи кой влиза, кога влиза и къде отива. Използвайки изкуствен интелект, тя определя дали всеки опит за достъп е нормален или съмнителен въз основа на модели като:

- Време на достъп (достъп през късна нощ срещу работни часове)
- Честота на достъп (твърде много опити за кратко време)
- Достъп до локация/стая (необичайни отдели)

Ако бъде открито съмнително поведение, системата сигнализира охраната и записва събитието. Цялата система е изградена чрез обектно-ориентирано програмиране в Python с графичен потребителски интерфейс (уеб приложение чрез Flask), SQLite база данни и функционалност за работа с файлове.

---

## 2. Описание на класовете

### Класове за данни

| Клас | Отговорности | Атрибути |
|-------|-----------------|------------|
| **User** | Представлява потребител, който осъществява достъп до системата | id, name, department, access_level, assigned_room |
| **AccessLog** | Записва всеки опит за достъп | id, user_id, access_time, location, status (granted/denied), attempts_count |
| **Alert** | Съхранява сигнали за сигурност | id, user_id, alert_type, description, created_at |

### Клас за AI/ML логика

| Клас | Отговорности | Методи |
|-------|-----------------|---------|
| **BehaviorAnalyzer** | Анализира модели на достъп чрез ML, класифицира като нормално или съмнително | analyze(), extract_features(), train_from_database(), save_model(), load_model(), retrain() |

### Класове Controller/Manager

| Клас | Отговорности | Методи |
|-------|-----------------|---------|
| **AccessController** | Обработва заявки за достъп, взема решения за разрешаване или отказ | request_access(), grant_access(), deny_access() |
| **SecurityManager** | Управлява сигнали за сигурност и наблюдава съмнителна дейност | handle_alert(), log_denied_access(), monitor_failed_attempts() |

### Клас за събития/Observer

| Клас | Отговорности | Методи |
|-------|-----------------|---------|
| **EventDispatcher** | Управлява регистрация и нотифициране на събития | register_listener(), unregister_listener(), dispatch_event() |

### Клас за работа с файлове

| Клас | Отговорности | Методи |
|-------|-----------------|---------|
| **FileManager** | Работи с четене/запис на JSON, CSV и лог файлове | write_log(), read_json(), write_json(), read_csv(), write_csv() |

### Клас за работа с база данни

| Клас | Отговорности | Методи |
|-------|-----------------|---------|
| **DatabaseManager** | Управлява SQLite база данни и CRUD операции | init_db(), create(), read(), update(), delete(), execute_query() |

### Класове за аргументи на събития

| Клас | Предназначение |
|-------|---------|
| **AccessEventArgs** | Съдържа данни за събития свързани с достъп |
| **AlertEventArgs** | Съдържа данни за сигнални събития |
| **SuspiciousBehaviorEventArgs** | Съдържа данни когато бъде открито съмнително поведение |

---

## 3. Файлова структура

```
AI-Access-Control-System/
├── app.py                    # Main Flask приложение
├── config.py                 # Конфигурационни настройки
├── requirements.txt          # Python зависимости
├── README.md                # Документация на проекта
├── docs/
│   ├── project_requirements.md
│   ├── project_topic.md
│   ├── phase1.md           # Този документ
│   └── phase2.md
├── data/
│   ├── sample_users.json   # Примерни потребителски данни
│   ├── sample_access.csv   # Примерни логове за достъп
│   └── logs/
│       └── system.log     # Системни логове
├── database/
│   └── database.py        # Инициализация на базата
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py        # Клас User
│   │   ├── access_log.py  # Клас AccessLog
│   │   └── alert.py       # Клас Alert
│   ├── ai/
│   │   ├── __init__.py
│   │   └── analyzer.py    # Клас BehaviorAnalyzer
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

## 4. Дизайн на базата данни

### SQLite База Данни: `access_control.db`

#### Таблица 1: users

| Колона | Тип | Ограничения | Описание |
|--------|------|-------------|--------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникален ID на потребител |
| name | TEXT | NOT NULL | Пълно име на потребител |
| department | TEXT | NOT NULL | Отдел на потребител |
| access_level | INTEGER | NOT NULL DEFAULT 1 | Ниво на достъп (1-5) |
| assigned_room | TEXT | | Определена стая/шкафче |

#### Таблица 2: access_logs

| Колона | Тип | Ограничения | Описание |
|--------|------|-------------|--------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникален ID на запис |
| user_id | INTEGER | FOREIGN KEY REFERENCES users(id) | Справка към потребител |
| access_time | TEXT | NOT NULL | Време на достъп |
| location | title | NOT NULL | Посетена стая/локац��я |
| status | TEXT | NOT NULL | "granted" или "denied" |
| attempts_count | INTEGER | DEFAULT 1 | Брой опити |

#### Таблица 3: alerts

| Колона | Тип | Ограничения | Описание |
|--------|------|-------------|--------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникален ID на сигнал |
| user_id | INTEGER | FOREIGN KEY REFERENCES users(id) | Справка към потребител |
| alert_type | TEXT | NOT NULL | Тип на сигнал |
| description | TEXT | | Описание на сигнала |
| created_at | TEXT | NOT NULL | Време на създаване на сигнала |

---

## 5. Дизайн на AI компонента (Използване на Machine Learning със sklearn)

### Клас BehaviorAnalyzer

AI компонентът използва **обучен модел за Machine Learning** (Decision Tree Classifier) от sklearn за класифициране на поведението като Нормално или Съмнително.

#### Как работи (Истински ML конвейер)

Моделът е **обучен върху таблицата access_logs** от SQLite базата данни. Всеки нов опит за достъп става обучителен запис.

**Обучителни данни - Характерики от таблици access_logs + users:**
| Характеристика | Описание | Диапазон на стойности | Таблица източник |
|---------|-------------|-------------|---------------|
| hour | Час на достъп (0-23) | 0-23 | access_logs (извлечена) |
| minute | Минута на достъп (0-59) | 0-59 | access_logs (извлечена) |
| day_of_week | Ден от седмицата (0=понеделник) | 0-6 | access_logs (извлечена) |
| is_weekend | Събота или неделя? | 0 или 1 | изчислена |
| access_count_last_hour | Опити в последните 60 мин | 0+ (неограничено) | access_logs (преброени) |
| is_assigned_room | Достъп до определената стая на потребителя? | 0 или 1 | users + access_logs |
| is_same_department | Стаята принадлежи ли на отдела на потребителя? | 0 или 1 | users + access_logs |
| user_access_level | Ниво на достъп на потребителя | 1-5 | users |
| historical_denied_count | Общ брой отказани опити на потребителя | 0+ | access_logs (преброени) |
| is_night_access | Достъп между 22:00-06:00? | 0 или 1 | изчислена |

**Целева променлива (Label):**
| Стойност | Значение |
|-------|---------|
| 0 | Нормално поведение |
| 1 | Съмнително поведение |

**Правило за етикиране (за обучителни данни):**
- Достъпът е "съмнителен" ако: нощен достъп ИЛИ повече от 3 опита/час ИЛИ достъп до грешна стая
- В противен случай: "нормален"

#### Поток на данни

```
1. Заявка за обучителни данни от базата
   SELECT * FROM access_logs JOIN users ON access_logs.user_id = users.id

2. Извличане на характеристики (за всеки запис)
    - Парсиране на access_time към час, минута, ден от седмицата
    - Брой опити в последния час за същия потребител
    - Проверка дали location == assigned_room
    - Проверка на съответствието на отдел
    - Преброяване на исторически откази

3. Създаване на етикети
    - Ако час >= 22 ИЛИ час < 6 → съмнителен (label=1)
    - Ако access_count_last_hour > 3 → съмнителен (label=1)
    - Ако НЕ is_assigned_room → съмнителен (label=1)
    - В противен случай → нормален (label=0)

4. Обучение на модела
    - X = характеристики (всички колони без етикета)
    - y = етикет
    - clf = DecisionTreeClassifier()
    - clf.fit(X, y)

5. Запазване и използване
    - pickle.dump(clf, open('model.pkl', 'wb'))
    - За прогнозиране на нови данни
```

#### Методи на AI

| Метод | Предназначение |
|--------|---------|
| analyze(user_id, access_time, location) | Главен анализ - извлича характеристики и прогнозира |
| extract_features(user_id, access_time, location) | Заявка към БД и изграждане на вектор от характеристики |
| get_access_frequency(user_id, time_window) | Брой опити в период от време (неограничено) |
| get_historical_denied_count(user_id) | Брой на всички отказани опити за потребител |
| is_assigned_room(user_id, location) | Проверка дали локацията съответства на определената стая |
| is_night_access(hour) | Проверка дали часът е нощен (22:00-06:00) |
| train_from_database() | Обучение на модела с текущите данни от access_logs |
| save_model(path) | Запазване на обучения модел във файл |
| load_model(path) | Зареждане на модела от файл |
| retrain() | Преобучение с актуализирани данни |

#### Пример за заявка към базата данни

```sql
-- Вземане на характеристики за обучение
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

#### Генериране на обучителни данни

Системата автоматично ще генерира обучителни данни от таблицата access_logs. За всеки запис:
- Извлича time характеристики от access_time
- Прави заявка към базата за честотни бройки
- Прилага правила за етикиране за създаване на етикети
- Това създава динамично обучение с реални данни

#### Поток на решение (при изпълнение)

1. AccessController получава заявка за достъп (user_id, access_time, location)
2. BehaviorAnalyzer.extract_features() прави заявка към базата
3. Изгражда вектор от характеристики: [hour, minute, day_of_week, is_weekend, access_count_last_hour, is_assigned_room, is_same_department, user_access_level, historical_denied_count, is_night_access]
4. Зарежда обучения модел
5. Извиква model.predict([features])
6. Връща "Normal" или "Suspicious"
7. AccessController решава: grant или deny
8. EventDispatcher нотифицира слушателите

#### Защо Decision Tree?

- **Интерпретируем**: Може да обясни взетото решение
- **Бърз**: Няма ��ло��ни изчисления
- **Работи с mixed данни**: Поддържа числови + категорийни данни
- **Подходящ за училищен проект**: Лесен за разбиране и обясняване
- **Динамично обучение**: Може да се преобучава от базата по всяко време

---

## 6. Примерни данни

### Примерни потребители (JSON)

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

### Обучителни данни

Моделът се обучава от **таблицата access_logs** в базата данни. Етикетите се генерират автоматично чрез правила:

**Правила за етикиране (за обучителни данни):**
- **Съмнителен (label=1)**: is_night_access OR access_count_last_hour > 3 OR NOT is_assigned_room
- **Нормален (label=0)**: В противен случай

**Примерни обучителни данни (автоматично генерирани от access_logs):**

| hour | minute | day_of_week | is_weekend | access_count_last_hour | is_assigned_room | is_same_department | user_access_level | historical_denied | is_night | label |
|------|--------|-------------|------------|-----------------------|-------------------|------------------|-------------------|------------------|-------------------|
| 9 | 30 | 0 | 0 | 1 | 1 | 1 | 3 | 0 | 0 | 0 |
| 14 | 15 | 0 | 0 | 1 | 1 | 1 | 2 | 0 | 0 | 0 |
| 23 | 45 | 0 | 0 | 1 | 1 | 1 | 3 | 0 | 1 | 1 |
| 10 | 0 | 5 | 0 | 5 | 1 | 1 | 2 | 0 | 0 | 1 |
| 3 | 20 | 6 | 1 | 3 | 0 | 0 | 1 | 2 | 1 | 1 |

**Забележка**: Системата се нуждае от поне 30 записа в access_logs за обучение. Новите потребители трябва да генерират множество опити за достъп с течение на времето.

### Примери за прогнозиране с ML модела

| access_time | location | Честота на достъп (последен час) | Определена стая | Отдел на потребител | Нощен? | ML Прогноза |
|------------|----------|---------------------|---------------|----------|-----------|--------------|
| Понеделник 09:30 | Room 101 | 1 | Room 101 | IT | Не | Normal |
| Понеделник 23:30 | Room 101 | 1 | Room 101 | IT | Да (23:30) | Suspicious |
| Събота 10:00 | Room 205 | 1 | Room 205 | HR | Не | Normal |
| Петък 02:00 | Room 302 | 3 | Room 302 | Finance | Да (02:00) | Suspicious |
| Вторник 14:00 | Room 101 | 5 | Room 101 | HR | Не | Suspicious |

Когато пристигне нов опит за достъп:
1. Системата прави заявка към access_logs за брой на честотата
2. Прави заявка към таблицата users за assigned_room и department
3. Извлича time характеристики (hour, minute, day_of_week)
4. Изгражда вектор от характеристики
5. Моделът прогнозира: "Normal" или "Suspicious"

---

## 7. Дизайн на събитията

### Събитие: on_suspicious_behavior

- **Тригер**: Когато BehaviorAnalyzer върне "Suspicious"
- **Слушатели**: SecurityManager, FileLogger
- **EventArgs**: SuspiciousBehaviorEventArgs (user_id, score, reason)

### Събитие: on_access_denied

- **Тригер**: Когато достъпът е отказан
- **Слушатели**: SecurityManager, AlertSystem
- **EventArgs**: AccessEventArgs (user_id, location, reason)

### Събитие: on_multiple_attempts

- **Тригер**: Повече от 3 опита за 1 час
- **Слушатели**: SecurityManager, DatabaseManager
- **EventArgs**: AlertEventArgs (user_id, attempts_count, time_window)

---

## 8. LINQ-подобни операции

Системата използва функционалните инструменти на Python:

| Операция | случай на използване |
|-----------|----------|
| `filter()` | Търсене на логове за достъп по период |
| `map()` | Извличане на имена на потребители от логове |
| `reduce()` | Изчисляване на общия брой опити за достъп |
| `sorted()` | Сортиране на потребители по брой достъпи |
| `groupby()` | Групиране на логове по локация |
| List comprehension | Търсене на модели на съмнително поведение |

---

## 9. Обработка на изключенията

| Изключение | Предназначение |
|-----------|---------|
| `DatabaseError` | Грешки при свързване/заявка към базата |
| `FileOperationError` | Грешки при четене/запис на файлове |
| `AIAnalysisError` | Грешки в AI модела |
| `ValidationError` | Грешки при валидация на входни данни |

---

## Резюме

Този документ от Фаза 1 дефинира:

- Пълната идея на проекта на разбираем език
- 6+ класа покриващи всички OOP изисквания
- Файлова структура за Flask уеб приложение
- Схема на базата данни с 3 таблици
- Предишно базирано на правила AI класифициране (старо)
+ Machine Learning използващо sklearn - обучава се от таблица access_logs в базата данни
- Примерни данни за тестване
- Архитектура базирана на събития
- LINQ-подобни операции с данни