import sqlite3
from sqlalchemy import create_engine, text

def local_db_connection(db_path="local.db"):
    return sqlite3.connect(db_path)

def cloud_db_connection(db_url):
    engine = create_engine(db_url)
    return engine.connect()

def sync_data(local_conn, cloud_conn):
    local_cursor = local_conn.cursor()
    local_cursor.execute("CREATE TABLE IF NOT EXISTS user_data (id TEXT PRIMARY KEY, data TEXT)")
    local_cursor.execute("SELECT * FROM user_data")
    rows = local_cursor.fetchall()
    for row in rows:
        cloud_conn.execute(text("INSERT INTO user_data (id, data) VALUES(:id, :data) "
                                "ON CONFLICT(id) DO UPDATE SET data = :data"),
                           {"id": row[0], "data": row[1]})
    return "Data synchronized successfully."