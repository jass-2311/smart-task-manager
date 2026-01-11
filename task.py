from database import connect

def add_task(uid,t,p,d):
    conn=connect();cur=conn.cursor()
    cur.execute('INSERT INTO tasks(user_id,title,priority,due_date) VALUES(?,?,?,?)',(uid,t,p,d))
    conn.commit();conn.close()

def view_tasks(uid):
    conn=connect();cur=conn.cursor()
    cur.execute('SELECT title,priority,due_date FROM tasks WHERE user_id=?',(uid,))
    r=cur.fetchall();conn.close();return r