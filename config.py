"""config.py — Application Configuration
Loads all settings from environment variables with sensible defaults.
Falls back to SQLite for local development if no DATABASE_URL is set.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
class Config:
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change')
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'csrf-dev-key')
    WTF_CSRF_ENABLED = True
    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key-please-change')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', 'False').lower() == 'true'
    JWT_COOKIE_CSRF_PROTECT = False
    # ── Database ──────────────────────────────────────────────────────────────
    # Falls back to local SQLite if DATABASE_URL is not set (great for dev)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'smart_attendance.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # ── Folders ───────────────────────────────────────────────────────────────
    EXPORT_FOLDER = os.path.join(BASE_DIR, os.environ.get('EXPORT_FOLDER', 'exports'))
    QR_FOLDER     = os.path.join(BASE_DIR, os.environ.get('QR_FOLDER', 'qr_codes'))
    # ── Session ───────────────────────────────────────────────────────────────
    SESSION_COOKIE_SECURE   = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATELIMIT_DEFAULT = '200 per day;50 per hour'
    RATELIMIT_STORAGE_URL = 'memory://'
    @staticmethod
    def init_app(app):
        """Create required directories on startup."""
        for folder in [Config.EXPORT_FOLDER, Config.QR_FOLDER]:
            os.makedirs(folder, exist_ok=True)
