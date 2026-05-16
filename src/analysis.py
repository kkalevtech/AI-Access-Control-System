from functools import reduce
from collections import defaultdict


def _parse_time(access_time):
    try:
        parts = access_time.split(':')
        return int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError, AttributeError):
        return None, None, None


def analyze_access_patterns(access_logs):
    if not access_logs:
        return {
            'total': 0,
            'granted': 0,
            'denied': 0,
            'success_rate': 0,
            'by_location': {},
            'by_day': {}
        }

    total = len(access_logs)
    granted = len(list(filter(lambda log: log.status == 'granted', access_logs)))
    denied = len(list(filter(lambda log: log.status == 'denied', access_logs)))
    success_rate = (granted / total * 100) if total > 0 else 0

    by_location = defaultdict(int)
    for log in access_logs:
        by_location[log.location] += 1

    by_day = defaultdict(int)
    for log in access_logs:
        is_weekend = getattr(log, 'is_weekend', 0)
        if is_weekend:
            by_day['Weekend'] += 1
        else:
            by_day['Weekday'] += 1

    return {
        'total': total,
        'granted': granted,
        'denied': denied,
        'success_rate': success_rate,
        'by_location': dict(by_location),
        'by_day': dict(by_day)
    }


def get_peak_access_hours(access_logs):
    if not access_logs:
        return []

    hour_counts = defaultdict(int)
    for log in access_logs:
        hour, _, _ = _parse_time(log.access_time)
        if hour is not None:
            hour_counts[hour] += 1

    hour_list = list(map(lambda x: {'hour': x[0], 'count': x[1]}, hour_counts.items()))
    sorted_hours = sorted(hour_list, key=lambda x: x['count'], reverse=True)

    return sorted_hours[:5] if len(sorted_hours) >= 5 else sorted_hours


def detect_anomalies(access_logs):
    if not access_logs:
        return {
            'high_frequency_users': [],
            'unusual_locations': [],
            'odd_time_patterns': []
        }

    user_counts = defaultdict(int)
    for log in access_logs:
        user_counts[log.user_id] += 1

    mean_count = reduce(lambda a, b: a + b, map(lambda x: x[1], user_counts.items()), 0) / len(user_counts) if user_counts else 0

    high_frequency_users = list(filter(
        lambda x: x[1] > mean_count * 3,
        user_counts.items()
    ))
    high_frequency_users = list(map(lambda x: {'user_id': x[0], 'count': x[1]}, high_frequency_users))

    location_counts = defaultdict(int)
    for log in access_logs:
        location_counts[log.location] += 1

    unusual_locations = list(filter(
        lambda x: x[1] <= 2,
        location_counts.items()
    ))
    unusual_locations = list(map(lambda x: {'location': x[0], 'count': x[1]}, unusual_locations))

    odd_time_patterns = []
    for user_id in user_counts:
        user_logs = list(filter(lambda log: log.user_id == user_id, access_logs))
        if len(user_logs) >= 3:
            hours = []
            for log in user_logs:
                hour, _, _ = _parse_time(log.access_time)
                if hour is not None:
                    hours.append(hour)

            if hours:
                unique_hours = len(set(hours))
                if unique_hours >= 20:
                    odd_time_patterns.append({
                        'user_id': user_id,
                        'unique_hours': unique_hours,
                        'description': 'Access at many different hours'
                    })

    return {
        'high_frequency_users': high_frequency_users,
        'unusual_locations': unusual_locations,
        'odd_time_patterns': odd_time_patterns
    }


def generate_access_report(db_manager, start_time=None, end_time=None):
    if start_time and end_time:
        logs = db_manager.get_access_logs_by_time_range(start_time, end_time)
    else:
        logs = db_manager.get_all_access_logs()

    patterns = analyze_access_patterns(logs)
    peak_hours = get_peak_access_hours(logs)
    anomalies = detect_anomalies(logs)

    most_active = db_manager.get_most_active_users(limit=5)

    return {
        'total_access_attempts': patterns['total'],
        'success_rate': patterns['success_rate'],
        'most_active_users': most_active,
        'peak_hours': peak_hours,
        'anomalies': anomalies,
        'by_location': patterns['by_location'],
        'by_day': patterns['by_day']
    }
