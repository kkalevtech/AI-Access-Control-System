import pytest
import os
import tempfile
from datetime import datetime, timedelta

from src.database.database_manager import DatabaseManager
from src.events.event_dispatcher import EventDispatcher
from src.ai.analyzer import BehaviorAnalyzer
from src.models import User, AccessLog


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    db = DatabaseManager(path)
    db.init_db()
    yield db
    db.close()
    os.unlink(path)


@pytest.fixture
def event_dispatcher():
    return EventDispatcher()


@pytest.fixture
def behavior_analyzer(temp_db):
    return BehaviorAnalyzer(temp_db)