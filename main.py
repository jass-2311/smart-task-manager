"""Start the terminal application with python main.py."""
from database import setup
from user import login, register
from task import add_task, view_tasks, get_task, update_task, delete_task

def task_menu(uid):
    while True:
        print("\n1 Add  2 List  3 Edit  4 Delete  5 Logout")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                task_id = add_task(uid, input("Title: "), input("Priority (low/medium/high): ").strip().lower(),
                                   input("Due date (optional): ").strip() or None)
                print(f"Created task #{task_id}")
            elif choice == "2":
                for item in view_tasks(uid):
                    print(f"#{item['id']} | {item['title']} | {item['priority']} | {item['due_date'] or '-'}")
            elif choice in ("3", "4"):
                task_id = int(input("Task ID: "))
                old = get_task(uid, task_id)
                if old is None:
                    print("Task not found.")
                    continue
                if choice == "4":
                    delete_task(uid, task_id)
                    print("Deleted.")
                else:
                    title = input(f"Title [{old['title']}]: ").strip() or old["title"]
                    priority = input(f"Priority [{old['priority']}]: ").strip().lower() or old["priority"]
                    due = input(f"Due date [{old['due_date'] or '-'}]: ").strip() or old["due_date"]
                    update_task(uid, task_id, title, priority, due)
                    print("Updated.")
            elif choice == "5":
                return
            else:
                print("Invalid choice.")
        except ValueError as error:
            print(f"Invalid input: {error}")

def main():
    setup()
    while True:
        print("\n1 Register  2 Login  3 Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            try:
                print("Registered." if register(input("Username: "), input("Password: ")) else "Username exists.")
            except ValueError as error:
                print(error)
        elif choice == "2":
            user = login(input("Username: "), input("Password: "))
            if user:
                print(f"Hello, {user[1]}!")
                task_menu(user[0])
            else:
                print("Invalid login.")
        elif choice == "3":
            break

if __name__ == "__main__":
    main()
