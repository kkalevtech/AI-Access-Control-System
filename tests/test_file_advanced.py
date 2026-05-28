import pytest
import os
import tempfile

from src.files.file_manager import FileManager
from src.database.database_manager import DatabaseManager
from src.models import User, AccessLog, Alert


@pytest.fixture
def file_manager():
    return FileManager()


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = DatabaseManager(path)
    db.init_db()
    yield db
    db.close()
    os.unlink(path)


class TestExportUsersToJson:
    def test_export_users(self, file_manager):
        users = [
            User(id=1, name="Alice", department="IT", access_level=3, assigned_room="IT-101"),
            User(id=2, name="Bob", department="HR", access_level=2, assigned_room="HR-201"),
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            filepath = f.name
        try:
            file_manager.export_users_to_json(filepath, users)
            data = file_manager.read_json(filepath)
            assert len(data) == 2
            assert data[0]['name'] == 'Alice'
        finally:
            os.unlink(filepath)


class TestExportAccessLogsToCsv:
    def test_export_logs(self, file_manager):
        logs = [
            AccessLog(id=1, user_id=1, access_time="2024-01-01", location="IT-101", status="granted"),
            AccessLog(id=2, user_id=2, access_time="2024-01-02", location="HR-201", status="denied"),
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
            filepath = f.name
        try:
            file_manager.export_access_logs_to_csv(filepath, logs)
            data = file_manager.read_csv(filepath)
            assert len(data) == 2
        finally:
            os.unlink(filepath)

    def test_export_empty_logs(self, file_manager):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
            filepath = f.name
        try:
            file_manager.export_access_logs_to_csv(filepath, [])
            assert os.path.exists(filepath)
        finally:
            os.unlink(filepath)


class TestImportUsersFromJson:
    def test_import_users(self, file_manager):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as f:
            f.write('[{"id": 1, "name": "Alice", "department": "IT", "access_level": 3, "assigned_room": "IT-101"}]')
            filepath = f.name
        try:
            users = file_manager.import_users_from_json(filepath)
            assert len(users) == 1
            assert users[0].name == 'Alice'
        finally:
            os.unlink(filepath)


class TestImportAccessLogsFromCsv:
    def test_import_logs(self, file_manager):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w') as f:
            f.write('id,user_id,access_time,location,status,attempts_count\n')
            f.write('1,1,2024-01-01,IT-101,granted,1\n')
            filepath = f.name
        try:
            logs = file_manager.import_access_logs_from_csv(filepath)
            assert len(logs) == 1
            assert logs[0].location == 'IT-101'
        finally:
            os.unlink(filepath)


class TestExportAlertsToJson:
    def test_export_alerts(self, file_manager):
        alerts = [
            Alert(id=1, user_id=1, alert_type='suspicious_behavior', description='Test alert', created_at='2024-01-01'),
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            filepath = f.name
        try:
            file_manager.export_alerts_to_json(filepath, alerts)
            data = file_manager.read_json(filepath)
            assert len(data) == 1
        finally:
            os.unlink(filepath)


class TestBackupRestoreDatabase:
    def test_backup_database(self, file_manager, temp_db):
        user = User(name="Test", department="IT", access_level=1, assigned_room="IT-101")
        temp_db.create_user(user)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            backup_path = f.name
        try:
            assert file_manager.backup_database(temp_db, backup_path) is True
            assert os.path.exists(backup_path)
        finally:
            os.unlink(backup_path)

    def test_restore_database(self, file_manager, temp_db):
        user = User(name="Original", department="IT", access_level=1, assigned_room="IT-101")
        user.id = temp_db.create_user(user)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            backup_path = f.name
        try:
            file_manager.backup_database(temp_db, backup_path)
            new_user = User(name="NewUser", department="HR", access_level=2, assigned_room="HR-201")
            temp_db.create_user(new_user)

            file_manager.restore_database(temp_db, backup_path)
            restored_user = temp_db.get_user(1)
            assert restored_user.name == "Original"
        finally:
            os.unlink(backup_path)


class TestErrorHandling:
    def test_import_nonexistent_file(self, file_manager):
        with pytest.raises(FileNotFoundError):
            file_manager.import_users_from_json('nonexistent.json')

    def test_import_invalid_json(self, file_manager):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as f:
            f.write('invalid json')
            filepath = f.name
        try:
            with pytest.raises(ValueError):
                file_manager.import_users_from_json(filepath)
        finally:
            os.unlink(filepath)