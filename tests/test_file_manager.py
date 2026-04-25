import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.files import FileManager


class TestFileManager:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.temp_files = []
        yield
        for f in self.temp_files:
            if os.path.exists(f):
                os.remove(f)

    def test_write_log(self):
        fm = FileManager()
        log_file = "test_system.log"
        self.temp_files.append(log_file)
        fm.write_log("Test message", log_file)
        lines = fm.read_log(log_file)
        assert len(lines) == 1
        assert "Test message" in lines[0]

    def test_read_log_nonexistent(self):
        fm = FileManager()
        lines = fm.read_log("nonexistent.log")
        assert lines == []

    def test_write_json(self):
        fm = FileManager()
        json_file = "test_data.json"
        self.temp_files.append(json_file)
        data = {"name": "John", "age": 30}
        fm.write_json(json_file, data)
        read_data = fm.read_json(json_file)
        assert read_data == data

    def test_read_json_nonexistent(self):
        fm = FileManager()
        with pytest.raises(FileNotFoundError):
            fm.read_json("nonexistent.json")

    def test_read_json_invalid(self):
        fm = FileManager()
        json_file = "test_invalid.json"
        self.temp_files.append(json_file)
        with open(json_file, "w") as f:
            f.write("{invalid json")
        with pytest.raises(ValueError):
            fm.read_json(json_file)

    def test_write_csv(self):
        fm = FileManager()
        csv_file = "test_data.csv"
        self.temp_files.append(csv_file)
        data = [{"name": "John", "age": "30"}, {"name": "Jane", "age": "25"}]
        fieldnames = ["name", "age"]
        fm.write_csv(csv_file, data, fieldnames)
        read_data = fm.read_csv(csv_file)
        assert len(read_data) == 2
        assert read_data[0]["name"] == "John"

    def test_read_csv_nonexistent(self):
        fm = FileManager()
        with pytest.raises(FileNotFoundError):
            fm.read_csv("nonexistent.csv")

    def test_read_csv_with_headers(self):
        fm = FileManager()
        csv_file = "test_with_headers.csv"
        self.temp_files.append(csv_file)
        with open(csv_file, "w", newline="") as f:
            f.write("name,age\nJohn,30\nJane,25\n")
        data = fm.read_csv(csv_file)
        assert len(data) == 2
        assert data[0]["name"] == "John"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])