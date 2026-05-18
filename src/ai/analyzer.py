from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
import pickle
import os


DEPT_PREFIX_MAP = {
    'FIN': 'Finance', 'HR': 'HR', 'IT': 'IT',
    'MKT': 'Marketing', 'OPS': 'Operations'
}


class BehaviorAnalyzer:
    def __init__(self, database):
        self.database = database
        self.model = RandomForestClassifier(random_state=42, n_estimators=100)
        self.is_trained = False

    def extract_features(self, user_id, access_time, location, is_weekend=0, reference_time=None):
        if isinstance(access_time, str) and ':' in access_time:
            parts = access_time.split(':')
            hour = int(parts[0])
            minute = int(parts[1])
        else:
            hour = 12
            minute = 0

        day_of_week = 6 if is_weekend else 0

        access_count_last_hour = self.get_access_frequency(user_id, 60, reference_time or access_time)

        user = self.database.get_user(user_id)
        if user:
            is_assigned = 1 if location == user.assigned_room else 0
            loc_prefix = location.split('-')[0] if '-' in location else location
            loc_dept = DEPT_PREFIX_MAP.get(loc_prefix, '')
            is_same_dept = 1 if loc_dept in user.departments else 0
            user_access_level = user.access_level
        else:
            is_assigned = 0
            is_same_dept = 0
            user_access_level = 1

        historical_denied = self.get_historical_denied_count(user_id)
        is_night = 1 if self.is_night_access(hour) else 0

        user_location_grant_rate = self.get_user_location_grant_rate(user_id, location)

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
            'is_night_access': is_night,
            'user_location_grant_rate': user_location_grant_rate
        }

    @staticmethod
    def _training_feature_vector(features):
        return [
            features['hour'], features['minute'], features['day_of_week'],
            features['is_weekend'], features['access_count_last_hour'],
            features['user_access_level'], features['historical_denied_count'],
            features['is_night_access'], features['user_location_grant_rate']
        ]

    def analyze(self, user_id, access_time, location, is_weekend=0):
        if not self.is_trained:
            return {
                'error': 'Model not trained. Call train_from_database() first.'
            }

        features = self.extract_features(user_id, access_time, location, is_weekend)
        feature_array = self._training_feature_vector(features)

        prediction = self.model.predict([feature_array])[0]
        proba = self.model.predict_proba([feature_array])[0]

        classification = "Suspicious" if prediction == 1 else "Normal"
        reason_data = self._generate_reason(features)

        return {
            'classification': classification,
            'confidence_normal': proba[0] * 100,
            'confidence_suspicious': proba[1] * 100,
            'reason': reason_data['all'],
            'normal_reasons': reason_data['normal'],
            'suspicious_reasons': reason_data['suspicious'],
            'user_id': user_id,
            'location': location,
            'timestamp': access_time
        }

    def get_prediction_confidence(self, features):
        feature_array = self._training_feature_vector(features)
        proba = self.model.predict_proba([feature_array])[0]
        return {
            'normal_prob': proba[0],
            'suspicious_prob': proba[1]
        }

    def get_access_frequency(self, user_id, time_window_minutes=60, reference_time_str=None):
        try:
            logs = self.database.get_user_access_logs(user_id)
            if not logs:
                return 0

            if reference_time_str is None:
                now = datetime.now()
                reference_time_str = now.strftime('%H:%M:%S')

            parts = reference_time_str.split(':')
            ref_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            cutoff_seconds = ref_seconds - time_window_minutes * 60
            if cutoff_seconds < 0:
                cutoff_seconds += 86400
            cutoff_h = cutoff_seconds // 3600
            cutoff_m = (cutoff_seconds % 3600) // 60
            cutoff_s = cutoff_seconds % 60
            cutoff_str = f"{cutoff_h:02d}:{cutoff_m:02d}:{cutoff_s:02d}"

            count = 0
            for log in logs:
                try:
                    if cutoff_str <= reference_time_str:
                        if cutoff_str <= log.access_time <= reference_time_str:
                            count += 1
                    else:
                        if log.access_time >= cutoff_str or log.access_time <= reference_time_str:
                            count += 1
                except (ValueError, AttributeError):
                    continue
            return count
        except Exception:
            return 0

    def get_historical_denied_count(self, user_id):
        try:
            logs = self.database.get_user_access_logs(user_id)
            if not logs:
                return 0
            return sum(1 for log in logs if log.status == 'denied')
        except Exception:
            return 0

    def is_assigned_room(self, user_id, location):
        user = self.database.get_user(user_id)
        if not user:
            return False
        return location == user.assigned_room

    def is_night_access(self, hour):
        return hour >= 22 or hour < 6

    def get_user_location_grant_rate(self, user_id, location):
        try:
            logs = self.database.get_user_access_logs(user_id)
            if not logs:
                return 0.5

            location_logs = [log for log in logs if log.location == location]
            if not location_logs:
                return 0.5

            granted = sum(1 for log in location_logs if log.status == 'granted')
            return granted / len(location_logs)
        except Exception:
            return 0.5

    def _generate_reason(self, features):
        normal_reasons = []
        suspicious_reasons = []

        if features['user_location_grant_rate'] > 0.7:
            normal_reasons.append(f"Previously granted at this location (rate: {features['user_location_grant_rate']:.0%})")
        elif features['user_location_grant_rate'] < 0.3 and features['user_location_grant_rate'] > 0:
            suspicious_reasons.append(f"Low historical grant rate ({features['user_location_grant_rate']:.0%})")
        elif features['user_location_grant_rate'] == 0.5:
            suspicious_reasons.append("No prior access history for this location")
        elif features['user_location_grant_rate'] > 0.3 and features['user_location_grant_rate'] <= 0.7:
            suspicious_reasons.append(f"Moderate grant rate ({features['user_location_grant_rate']:.0%}) at this location")

        if features['is_night_access'] == 1:
            suspicious_reasons.append("Access during night hours (22:00-06:00)")
        else:
            normal_reasons.append(f"Access during normal hours ({features['hour']:02d}:00)")

        if features['access_count_last_hour'] > 3:
            suspicious_reasons.append(f"High access frequency ({features['access_count_last_hour']} attempts in last hour)")
        elif features['access_count_last_hour'] > 0:
            normal_reasons.append(f"Moderate access frequency ({features['access_count_last_hour']} attempts in last hour)")
        else:
            normal_reasons.append("Low access frequency (no recent attempts)")

        if features['is_assigned_room'] == 1:
            normal_reasons.append("User is accessing their assigned room")
        else:
            suspicious_reasons.append("Not user's assigned room")

        if features['is_same_department'] == 1:
            normal_reasons.append("Department authorization matches this area")
        else:
            suspicious_reasons.append("No department authorization for this area")

        if features['historical_denied_count'] > 5:
            suspicious_reasons.append(f"User has {features['historical_denied_count']} historical denied attempts")
        elif features['historical_denied_count'] > 0:
            suspicious_reasons.append(f"User has {features['historical_denied_count']} historical denied attempts")
        else:
            normal_reasons.append("No historical denied attempts")

        return {
            'normal': normal_reasons,
            'suspicious': suspicious_reasons,
            'all': "; ".join(normal_reasons + suspicious_reasons) if normal_reasons or suspicious_reasons else "No unusual patterns detected"
        }

    def train_from_database(self):
        try:
            all_logs = self.database.get_all_access_logs()
            if not all_logs or len(all_logs) < 30:
                return {'error': 'Insufficient data. Need at least 30 access logs.'}

            X = []
            y = []

            for log in all_logs:
                try:
                    features = self.extract_features(
                        log.user_id, log.access_time, log.location,
                        getattr(log, 'is_weekend', 0),
                        reference_time=log.access_time
                    )

                    is_suspicious = 1 if log.status == 'denied' else 0

                    X.append(self._training_feature_vector(features))
                    y.append(is_suspicious)
                except Exception:
                    continue

            if len(X) < 30:
                return {'error': 'Insufficient valid samples for training.'}

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            self.model.fit(X_train, y_train)
            self.is_trained = True

            train_acc = self.model.score(X_train, y_train)
            test_acc = self.model.score(X_test, y_test)

            cv_scores = cross_val_score(self.model, X, y, cv=5)
            cv_mean = cv_scores.mean()

            return {
                'num_samples': len(X),
                'test_accuracy': test_acc,
                'train_accuracy': train_acc,
                'cross_val_accuracy': cv_mean,
                'test_samples': len(X_test),
                'train_samples': len(X_train)
            }
        except Exception as e:
            return {'error': str(e)}

    def save_model(self, filepath="model.pkl"):
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({'model': self.model, 'is_trained': self.is_trained}, f)
            return True
        except Exception:
            return False

    def load_model(self, filepath="model.pkl"):
        try:
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.is_trained = data['is_trained']
            return True
        except Exception:
            return False

    def retrain(self):
        return self.train_from_database()
