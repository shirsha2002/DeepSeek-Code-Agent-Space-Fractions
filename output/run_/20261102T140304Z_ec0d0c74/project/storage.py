import os
import sqlite3
import hashlib
import secrets
from contextlib import closing
from fractions import Fraction
from game_core import Question

def get_app_data_dir():
    """Return per-user application data directory, creating it if needed."""
    base = os.environ.get('APPDATA') or os.path.expanduser('~')
    data_dir = os.path.join(base, 'SpaceFractions')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def init_db(db_path):
    """Create tables if they do not exist."""
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    qid TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    options TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    explanation TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    score INTEGER NOT NULL,
                    total INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    salt TEXT NOT NULL,
                    hash TEXT NOT NULL
                )
            ''')

def save_question(db_path, question):
    """Save or replace a Question."""
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute('''
                INSERT INTO questions (qid, prompt, options, answer, explanation)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(qid) DO UPDATE SET
                    prompt = excluded.prompt,
                    options = excluded.options,
                    answer = excluded.answer,
                    explanation = excluded.explanation
            ''', (question.qid, question.prompt,
                   '|'.join(question.options), question.answer, question.explanation))

def get_questions(db_path):
    """Return list of Question objects from DB."""
    questions = []
    with closing(sqlite3.connect(db_path)) as conn:
        rows = conn.execute('SELECT qid, prompt, options, answer, explanation FROM questions ORDER BY qid').fetchall()
    for row in rows:
        qid, prompt, options_str, answer, explanation = row
        options = options_str.split('|')
        try:
            q = Question(qid, prompt, options, answer, explanation)
            questions.append(q)
        except ValueError:
            pass
    return questions

def save_score(db_path, score, total):
    """Insert a score record."""
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute('INSERT INTO scores (score, total) VALUES (?, ?)', (score, total))

def get_score_history(db_path, limit=10):
    """Return list of (score, total, played_at) tuples, most recent first."""
    with closing(sqlite3.connect(db_path)) as conn:
        rows = conn.execute('SELECT score, total, played_at FROM scores ORDER BY played_at DESC, id DESC LIMIT ?', (limit,)).fetchall()
    return rows

def _hash_password(password, salt):
    """Hash password with salt using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

def admin_create(db_path, password):
    """Create admin account if none exists. Returns True if created, False if already exists."""
    salt = secrets.token_hex(16)
    hashed = _hash_password(password, bytes.fromhex(salt))
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            exists = conn.execute('SELECT COUNT(*) FROM admin').fetchone()[0]
            if exists:
                return False
            conn.execute('INSERT INTO admin (salt, hash) VALUES (?, ?)', (salt, hashed))
            return True

def admin_authenticate(db_path, password):
    """Check password against stored admin. Returns True if valid, False otherwise."""
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute('SELECT salt, hash FROM admin LIMIT 1').fetchone()
    if not row:
        return False
    salt_hex, stored_hash = row
    salt = bytes.fromhex(salt_hex)
    computed = _hash_password(password, salt)
    return computed == stored_hash

def admin_exists(db_path):
    """Return True if an admin account exists."""
    with closing(sqlite3.connect(db_path)) as conn:
        count = conn.execute('SELECT COUNT(*) FROM admin').fetchone()[0]
    return count > 0
