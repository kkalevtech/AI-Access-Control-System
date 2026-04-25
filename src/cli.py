import os
import sys
from src.database import DatabaseManager
from src.events import EventDispatcher
from src.controllers import AccessController, SecurityManager
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "access_control.db")


class CLI:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.db = DatabaseManager(DB_PATH)
        self.db.init_db()
        self.dispatcher = EventDispatcher()
        self.access_controller = AccessController(self.db, self.dispatcher)
        self.security_manager = SecurityManager(self.db, self.dispatcher)

        self.dispatcher.register_listener('on_suspicious_behavior', self.security_manager.on_suspicious_behavior_handler)
        self.dispatcher.register_listener('on_access_denied', self.security_manager.on_access_denied_handler)
        self.dispatcher.register_listener('on_multiple_attempts', self.security_manager.on_multiple_attempts_handler)

    def parse_command(self, line):
        parts = line.strip().split()
        if not parts:
            return None, []

        cmd = parts[0]
        args = parts[1:]
        return cmd, args

    def add_user(self, args):
        if len(args) < 3:
            print("Usage: add_user <name> <department> <access_level> [assigned_room]")
            return

        name = args[0]
        department = args[1]
        access_level = int(args[2])
        assigned_room = args[3] if len(args) > 3 else None

        user = type('User', (), {
            'name': name,
            'department': department,
            'access_level': access_level,
            'assigned_room': assigned_room
        })()

        user_id = self.db.create_user(user)
        print(f"User created with ID: {user_id}")

    def list_users(self, args):
        users = self.db.get_all_users()
        if not users:
            print("No users found.")
            return

        print(f"{'ID':<5} {'Name':<20} {'Department':<15} {'Access Level':<12} {'Assigned Room'}")
        print("-" * 70)
        for user in users:
            print(f"{user.id:<5} {user.name:<20} {user.department:<15} {user.access_level:<12} {user.assigned_room or ''}")

    def add_access_log(self, args):
        if len(args) < 3:
            print("Usage: add_access_log <user_id> <location> <status>")
            return

        user_id = int(args[0])
        location = args[1]
        status = args[2]

        from datetime import datetime
        access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log = type('Log', (), {
            'user_id': user_id,
            'access_time': access_time,
            'location': location,
            'status': status,
            'attempts_count': 1
        })()

        log_id = self.db.create_access_log(log)
        print(f"Access log created with ID: {log_id}")

    def list_access_logs(self, args):
        if args:
            user_id = int(args[0])
            logs = self.db.get_user_access_logs(user_id)
        else:
            logs = self.db.get_all_access_logs()

        if not logs:
            print("No access logs found.")
            return

        print(f"{'ID':<5} {'User ID':<8} {'Access Time':<20} {'Location':<15} {'Status':<10} {'Attempts'}")
        print("-" * 75)
        for log in logs:
            print(f"{log.id:<5} {log.user_id:<8} {log.access_time:<20} {log.location:<15} {log.status:<10} {log.attempts_count}")

    def request_access(self, args):
        if len(args) < 2:
            print("Usage: request_access <user_id> <location>")
            return

        user_id = int(args[0])
        location = args[1]

        result = self.access_controller.request_access(user_id, location)

        if result['granted']:
            print(f"ACCESS GRANTED: User {user_id} to {location}")
            print(f"Reason: {result['reason']}")
        else:
            print(f"ACCESS DENIED: User {user_id} to {location}")
            print(f"Reason: {result['reason']}")

    def list_alerts(self, args):
        if args:
            user_id = int(args[0])
            alerts = self.db.get_user_alerts(user_id)
        else:
            alerts = self.db.get_all_alerts()

        if not alerts:
            print("No alerts found.")
            return

        print(f"{'ID':<5} {'User ID':<8} {'Alert Type':<20} {'Description':<30} {'Created At'}")
        print("-" * 90)
        for alert in alerts:
            desc = alert.description[:27] + "..." if alert.description and len(alert.description) > 30 else alert.description or ""
            print(f"{alert.id:<5} {alert.user_id:<8} {alert.alert_type:<20} {desc:<30} {alert.created_at}")

    def run(self):
        print("Access Control System CLI")
        print("Commands: add_user, list_users, add_access_log, list_access_logs, request_access, list_alerts, exit")

        while True:
            try:
                line = input("\n> ")
                if not line:
                    continue

                cmd, args = self.parse_command(line)

                if cmd == "add_user":
                    self.add_user(args)
                elif cmd == "list_users":
                    self.list_users(args)
                elif cmd == "add_access_log":
                    self.add_access_log(args)
                elif cmd == "list_access_logs":
                    self.list_access_logs(args)
                elif cmd == "request_access":
                    self.request_access(args)
                elif cmd == "list_alerts":
                    self.list_alerts(args)
                elif cmd == "exit":
                    print("Exiting...")
                    break
                else:
                    print(f"Unknown command: {cmd}")
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

        self.db.close()


if __name__ == "__main__":
    cli = CLI()
    cli.run()