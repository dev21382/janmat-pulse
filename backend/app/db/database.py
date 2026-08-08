import sqlite3
import threading
from contextlib import contextmanager

from app.config import DB_PATH

_local = threading.local()
_schema_path = DB_PATH.parent.parent / "app" / "db" / "schema.sql"


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_conn():
    if not hasattr(_local, "conn"):
        _local.conn = _connect()
    return _local.conn


@contextmanager
def cursor():
    conn = get_conn()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def init_db():
    schema = _schema_path.read_text()
    conn = _connect()
    conn.executescript(schema)
    conn.commit()
    conn.close()
