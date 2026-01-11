import sqlite3

def connect():
    return sqlite3.connect('tasks.db')

def setup():
    conn=connect();cur=conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, title TEXT, priority TEXT, due_date TEXT)')
    conn.commit();conn.close()