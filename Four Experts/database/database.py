import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "resume.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def getLLMRoles():
    """جلب كافة أدوار الخبراء والمحفزات من قاعدة البيانات"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role_name, system_prompt FROM llm_roles")
    roles = cursor.fetchall()
    conn.close()
    return [dict(role) for role in roles]

def insertRows(table_name, rows_data):
    """إدخال بيانات جديدة إلى أي جدول"""
    if not rows_data:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = ', '.join(rows_data[0].keys())
    placeholders = ', '.join(['?'] * len(rows_data[0]))
    
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    for row in rows_data:
        cursor.execute(sql, list(row.values()))
        
    conn.commit()
    conn.close()