import sqlite3
import pandas as pd

def connect_to_database(db_path):
    if db_path.lower().endswith('.sql'):
        conn = sqlite3.connect(':memory:')
        with open(db_path, 'r') as sql_file:
            sql_script = sql_file.read()
        try:
            conn.executescript(sql_script)
        except sqlite3.Error as e:
            raise ValueError(f"Error executing SQL script: {str(e)}")
    else:
        try:
            conn = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            raise ValueError(f"Error connecting to the database: {str(e)}")
    return conn

def create_test_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary REAL
    )
    ''')

    sample_data = [
        (1, 'John Doe', 'IT', 75000),
        (2, 'Jane Smith', 'HR', 65000),
        (3, 'Mike Johnson', 'Sales', 80000),
        (4, 'Emily Brown', 'Marketing', 70000)
    ]
    cursor.executemany('INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?)', sample_data)
    conn.commit()

def get_table_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def get_table_data(conn, table_name):
    return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

def execute_query(conn, query):
    return pd.read_sql_query(query, conn)

def list_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

