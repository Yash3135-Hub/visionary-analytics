import sqlite3
from datetime import datetime, timedelta
from config import DB_NAME
from utils import hash_password

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 2


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        failed_attempts INTEGER DEFAULT 0,
        locked_until TEXT,
        role TEXT DEFAULT 'user'
    )
    """)
    conn.commit()

    # Migrations
    for column_def in ["email TEXT", "failed_attempts INTEGER DEFAULT 0", "locked_until TEXT", "role TEXT DEFAULT 'user'"]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_def}")
            conn.commit()
        except sqlite3.OperationalError:
            pass

    # Upload history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS upload_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        filename TEXT,
        upload_date TEXT,
        total_rows INTEGER
    )
    """)
    conn.commit()

    # Seed Default Admin if no admin exists
    cursor.execute("SELECT id FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users(username, password, email, role) VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "admin@visionary.com", "admin")
        )
        conn.commit()

    conn.close()


def register_user(username, password, email, role="user"):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            conn.close()
            return "USERNAME_EXISTS"

        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            conn.close()
            return "EMAIL_EXISTS"

        cursor.execute(
            "INSERT INTO users(username,password,email,role) VALUES (?,?,?,?)",
            (username, hash_password(password), email, role)
        )
        conn.commit()
        conn.close()
        return "SUCCESS"
    except Exception as e:
        print("Registration Error:", e)
        return "DB_ERROR"


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_role(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else "user"


def get_email_for_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else None


def update_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password=? WHERE username=?",
        (hash_password(new_password), username)
    )
    conn.commit()
    conn.close()


# ---------------- LOGIN ATTEMPT LOCKOUT ----------------

def check_lockout(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT locked_until FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return 0

    try:
        locked_until = datetime.fromisoformat(row[0])
        remaining = (locked_until - datetime.now()).total_seconds()
        return max(0, int(remaining))
    except Exception:
        return 0


def record_failed_attempt(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT failed_attempts FROM users WHERE username=?", (username,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    attempts = (row[0] or 0) + 1

    if attempts >= MAX_FAILED_ATTEMPTS:
        locked_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
        cursor.execute(
            "UPDATE users SET failed_attempts=?, locked_until=? WHERE username=?",
            (attempts, locked_until, username)
        )
    else:
        cursor.execute(
            "UPDATE users SET failed_attempts=? WHERE username=?",
            (attempts, username)
        )

    conn.commit()
    conn.close()
    return MAX_FAILED_ATTEMPTS - attempts


def reset_login_attempts(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET failed_attempts=0, locked_until=NULL WHERE username=?",
        (username,)
    )
    conn.commit()
    conn.close()


# ---------------- UPLOAD HISTORY ----------------

def record_upload(username, filename, total_rows):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO upload_history(username, filename, upload_date, total_rows) VALUES (?,?,?,?)",
        (username, filename, datetime.now().strftime("%Y-%m-%d %H:%M"), total_rows)
    )
    conn.commit()
    conn.close()


def get_upload_history(username, limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, upload_date, total_rows FROM upload_history "
        "WHERE username=? ORDER BY id DESC LIMIT ?",
        (username, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- ADMIN PANEL ----------------

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    # Query updated to fetch newly registered users at top and handle Null values cleanly
    cursor.execute(
        "SELECT username, email, COALESCE(role, 'user'), COALESCE(failed_attempts, 0), COALESCE(locked_until, 'None') "
        "FROM users ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_uploads(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, filename, upload_date, total_rows FROM upload_history "
        "ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_admin_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM upload_history")
    total_uploads = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE locked_until IS NOT NULL AND locked_until != '' AND locked_until != 'None'"
    )
    locked_accounts = cursor.fetchone()[0]

    conn.close()
    return total_users, total_uploads, locked_accounts


def set_user_role(username, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role=? WHERE username=?", (role, username))
    conn.commit()
    conn.close()


def unlock_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET failed_attempts=0, locked_until=NULL WHERE username=?",
        (username,)
    )
    conn.commit()
    conn.close()


def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    cursor.execute("DELETE FROM upload_history WHERE username=?", (username,))
    conn.commit()
    conn.close()
