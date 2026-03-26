from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import shutil
import sys
import threading
import webbrowser
from functools import partial
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
DATA_FILE = BASE_DIR / "storage" / "students.json"
USERS_FILE = BASE_DIR / "storage" / "users.json"
BACKUP_DIR = BASE_DIR / "storage" / "backups"
DEFAULT_PORT = 8030
SESSION_COOKIE = "student_analysis_session"
SESSION_STORE: dict[str, str] = {}
MAX_BACKUPS = 5


def predict_score(hours: float, sessions: int, planned: int, completed: int, difficulty: int) -> tuple[float, float]:
    completion_rate = (completed / planned) if planned else 0
    base_score = (hours * 2) + (sessions * 3)
    completion_score = completion_rate * 50
    difficulty_bonus = difficulty * 5

    score = base_score + completion_score + difficulty_bonus

    if completion_rate < 0.5:
        score -= 20
    if completion_rate < 0.3:
        score -= 30
    if difficulty == 3 and completion_rate < 0.5:
        score -= 10

    score = max(0, min(score, 100))
    return round(score, 2), round(completion_rate * 100, 2)


def give_feedback(score: float) -> str:
    if score >= 80:
        return "Excellent! You studied effectively and completed your goals."
    if score >= 65:
        return "Good effort, but improve completion."
    if score >= 50:
        return "You studied, but did not complete enough work."
    return "Poor performance. Focus on finishing what you start."


def users_file_is_valid(path: Path) -> bool:
    if not path.exists():
        return False

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return False

    return isinstance(data, dict)


def users_file_has_data(path: Path) -> bool:
    if not users_file_is_valid(path):
        return False

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return bool(data)


def students_file_is_valid(path: Path) -> bool:
    if not path.exists():
        return False

    try:
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()
                if not stripped:
                    continue
                json.loads(stripped)
    except (OSError, json.JSONDecodeError):
        return False

    return True


def students_file_has_data(path: Path) -> bool:
    if not students_file_is_valid(path):
        return False

    with path.open("r", encoding="utf-8") as file:
        return any(line.strip() for line in file)


def backup_name_for(path: Path, suffix: str) -> Path:
    return BACKUP_DIR / f"{path.stem}.{suffix}.bak"


def cleanup_old_backups(path: Path) -> None:
    pattern = f"{path.stem}.snapshot-*.bak"
    backups = sorted(BACKUP_DIR.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    for backup in backups[MAX_BACKUPS:]:
        backup.unlink(missing_ok=True)


def create_backup(path: Path) -> None:
    if not path.exists():
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_name_for(path, "latest"))
    snapshot_name = f"snapshot-{int(path.stat().st_mtime_ns)}"
    shutil.copy2(path, backup_name_for(path, snapshot_name))
    cleanup_old_backups(path)


def restore_from_backup(path: Path) -> bool:
    if path == USERS_FILE:
        validator = users_file_is_valid
    else:
        validator = students_file_is_valid

    latest_backup = backup_name_for(path, "latest")
    candidates = [latest_backup]
    candidates.extend(
        sorted(
            BACKUP_DIR.glob(f"{path.stem}.snapshot-*.bak"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
    )

    for backup in candidates:
        if not backup.exists() or not validator(backup):
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, path)
        return True

    return False


def ensure_storage_file(path: Path) -> None:
    if path == USERS_FILE:
        validator = users_file_is_valid
        has_data = users_file_has_data
        default_content = "{}\n"
    else:
        validator = students_file_is_valid
        has_data = students_file_has_data
        default_content = ""

    if validator(path):
        latest_backup = backup_name_for(path, "latest")
        if not has_data(path) and latest_backup.exists() and has_data(latest_backup):
            restore_from_backup(path)
        return

    restored = restore_from_backup(path)
    if restored and validator(path):
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(default_content, encoding="utf-8")


def write_json_atomic(path: Path, payload: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
        file.write("\n")
    temp_path.replace(path)
    create_backup(path)


def save_student_record(hours: float, sessions: int, completed: int, score: float) -> None:
    record = {
        "hours": hours,
        "sessions": sessions,
        "completed_pages": completed,
        "predicted_score": score,
    }

    ensure_storage_file(DATA_FILE)
    with DATA_FILE.open("a", encoding="utf-8") as file:
        json.dump(record, file)
        file.write("\n")
    create_backup(DATA_FILE)


def load_users() -> dict[str, dict[str, str]]:
    ensure_storage_file(USERS_FILE)

    with USERS_FILE.open("r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return {}

    if not isinstance(data, dict):
        return {}

    return data


def save_users(users: dict[str, dict[str, str]]) -> None:
    write_json_atomic(USERS_FILE, users)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str, salt: bytes | None = None) -> str:
    actual_salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), actual_salt, 100_000)
    return f"{base64.b64encode(actual_salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, stored_value: str) -> bool:
    try:
        salt_b64, digest_b64 = stored_value.split("$", 1)
        salt = base64.b64decode(salt_b64.encode())
        expected_digest = base64.b64decode(digest_b64.encode())
    except (ValueError, TypeError):
        return False

    candidate_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hmac.compare_digest(candidate_digest, expected_digest)


def get_session_email(handler: "StudentAnalysisHandler") -> str | None:
    cookie_header = handler.headers.get("Cookie")
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    morsel = cookie.get(SESSION_COOKIE)
    if morsel is None:
        return None

    return SESSION_STORE.get(morsel.value)


class StudentAnalysisHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_POST(self) -> None:
        if self.path == "/api/register":
            self._handle_register()
            return

        if self.path == "/api/login":
            self._handle_login()
            return

        if self.path == "/api/logout":
            self._handle_logout()
            return

        if self.path != "/api/analyze":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        session_email = get_session_email(self)
        if not session_email:
            self._send_json({"error": "Please log in first."}, HTTPStatus.UNAUTHORIZED)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))

            hours = float(payload["hours"])
            sessions = int(payload["sessions"])
            planned = int(payload["planned"])
            completed = int(payload["completed"])
            difficulty = int(payload["difficulty"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._send_json({"error": "Please enter valid study details."}, HTTPStatus.BAD_REQUEST)
            return

        if hours < 0 or sessions < 0 or planned < 0 or completed < 0:
            self._send_json({"error": "Values cannot be negative."}, HTTPStatus.BAD_REQUEST)
            return

        if difficulty not in {1, 2, 3}:
            self._send_json({"error": "Difficulty must be 1, 2, or 3."}, HTTPStatus.BAD_REQUEST)
            return

        score, completion_rate = predict_score(hours, sessions, planned, completed, difficulty)
        feedback = give_feedback(score)
        warning = "Low completion rate significantly reduced your score." if completion_rate < 50 else ""

        save_student_record(hours, sessions, completed, score)

        self._send_json(
            {
                "score": score,
                "completionRate": completion_rate,
                "feedback": feedback,
                "warning": warning,
                "email": session_email,
            },
            HTTPStatus.OK,
        )

    def do_GET(self) -> None:
        if self.path == "/api/session":
            session_email = get_session_email(self)
            if not session_email:
                self._send_json({"authenticated": False}, HTTPStatus.OK)
                return

            self._send_json(
                {"authenticated": True, "email": session_email},
                HTTPStatus.OK,
            )
            return

        super().do_GET()

    def _read_json_payload(self) -> dict[str, object]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(raw_body) if raw_body else {}

    def _handle_register(self) -> None:
        try:
            payload = self._read_json_payload()
            email = normalize_email(str(payload["email"]))
            password = str(payload["password"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._send_json({"error": "Please enter a valid email and password."}, HTTPStatus.BAD_REQUEST)
            return

        if "@" not in email or "." not in email:
            self._send_json({"error": "Please enter a valid email address."}, HTTPStatus.BAD_REQUEST)
            return

        if len(password) < 6:
            self._send_json({"error": "Password must be at least 6 characters."}, HTTPStatus.BAD_REQUEST)
            return

        users = load_users()
        if email in users:
            self._send_json({"error": "This email is already registered. Please log in."}, HTTPStatus.CONFLICT)
            return

        users[email] = {"password_hash": hash_password(password)}
        save_users(users)
        self._create_session(email)
        self._send_json({"message": "Account created successfully.", "email": email}, HTTPStatus.CREATED)

    def _handle_login(self) -> None:
        try:
            payload = self._read_json_payload()
            email = normalize_email(str(payload["email"]))
            password = str(payload["password"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._send_json({"error": "Please enter your email and password."}, HTTPStatus.BAD_REQUEST)
            return

        users = load_users()
        user = users.get(email)
        if not user or not verify_password(password, user.get("password_hash", "")):
            self._send_json({"error": "Incorrect email or password."}, HTTPStatus.UNAUTHORIZED)
            return

        self._create_session(email)
        self._send_json({"message": "Login successful.", "email": email}, HTTPStatus.OK)

    def _handle_logout(self) -> None:
        cookie_header = self.headers.get("Cookie")
        if cookie_header:
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            morsel = cookie.get(SESSION_COOKIE)
            if morsel is not None:
                SESSION_STORE.pop(morsel.value, None)

        self._send_json({"message": "Logged out."}, HTTPStatus.OK, self._expired_cookie_header())

    def _create_session(self, email: str) -> None:
        token = secrets.token_urlsafe(24)
        SESSION_STORE[token] = email
        self._session_cookie_header = self._build_cookie_header(token)

    def _build_cookie_header(self, token: str) -> str:
        return f"{SESSION_COOKIE}={token}; HttpOnly; Path=/; SameSite=Lax"

    def _expired_cookie_header(self) -> str:
        return f"{SESSION_COOKIE}=; HttpOnly; Path=/; Max-Age=0; SameSite=Lax"

    def _send_json(self, payload: dict[str, object], status: HTTPStatus, set_cookie: str | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        pending_cookie = set_cookie or getattr(self, "_session_cookie_header", None)
        if pending_cookie:
            self.send_header("Set-Cookie", pending_cookie)
            if hasattr(self, "_session_cookie_header"):
                delattr(self, "_session_cookie_header")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        super().log_message(format, *args)


def open_browser(port: int) -> None:
    url = f"http://127.0.0.1:{port}/"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()


def run(port: int = DEFAULT_PORT) -> None:
    ensure_storage_file(USERS_FILE)
    ensure_storage_file(DATA_FILE)
    create_backup(USERS_FILE)
    create_backup(DATA_FILE)
    handler = partial(StudentAnalysisHandler, directory=str(WEB_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Student Analysis web app running at http://127.0.0.1:{port}/")
    print("Press Ctrl+C to stop the server")
    open_browser(port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    selected_port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    run(selected_port)
