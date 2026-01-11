from database import connect

def register(u,p):
    conn=connect();cur=conn.cursor()
    try:
        cur.execute('INSERT INTO users(username,password) VALUES(?,?)',(u,p));conn.commit();return True
    except: return False
    finally: conn.close()

def login(u,p):
    conn=connect();cur=conn.cursor()
    cur.execute('SELECT id FROM users WHERE username=? AND password=?',(u,p))
    r=cur.fetchone();conn.close();return r