from database import setup
from user import register,login
from task import add_task,view_tasks

setup()
print('=== Smart Task Manager ===')
while True:
    print('\n1.Register\n2.Login\n3.Exit')
    c=input('Choose: ')
    if c=='1':
        u=input('Username: ');p=input('Password: ')
        print('Account created.' if register(u,p) else 'Username exists.')
    elif c=='2':
        u=input('Username: ');p=input('Password: ')
        user=login(u,p)
        if user:
            uid=user[0];print('Logged in!')
            while True:
                print('\n1.Add Task\n2.View Tasks\n3.Logout')
                k=input('Choose: ')
                if k=='1': add_task(uid,input('Title: '),input('Priority: '),input('Due: '))
                elif k=='2':
                    for t in view_tasks(uid): print(f"{t[0]} | {t[1]} | {t[2]}")
                else: break
        else: print('Invalid login')
    else: break