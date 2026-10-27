"""Local demo REST API; HTTP Basic requires HTTPS if deployed."""
from contextlib import asynccontextmanager
from datetime import date
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from database import setup
from user import login, register
from task import add_task, view_tasks, get_task, update_task, delete_task

@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup()
    yield

app = FastAPI(title="Smart Task Manager API", lifespan=lifespan)
security = HTTPBasic()

class Account(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8)

class TaskInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    priority: Literal["low", "medium", "high"] = "medium"
    due_date: date | None = None

class TaskOutput(TaskInput):
    id: int

def current_user(credentials: HTTPBasicCredentials = Depends(security)):
    found = login(credentials.username, credentials.password)
    if found is None:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"})
    return found[0]

@app.post("/users", status_code=201)
def create_user(data: Account):
    try:
        created = register(data.username, data.password)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if not created:
        raise HTTPException(status_code=409, detail="Username already exists")
    return {"message": "User registered"}

@app.get("/tasks", response_model=list[TaskOutput])
def list_tasks(uid: int = Depends(current_user)):
    return view_tasks(uid)

@app.post("/tasks", status_code=201, response_model=TaskOutput)
def create_task(data: TaskInput, uid: int = Depends(current_user)):
    task_id = add_task(uid, data.title, data.priority, data.due_date.isoformat() if data.due_date else None)
    return get_task(uid, task_id)

@app.get("/tasks/{task_id}", response_model=TaskOutput)
def read_task(task_id: int, uid: int = Depends(current_user)):
    item = get_task(uid, task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return item

@app.put("/tasks/{task_id}", response_model=TaskOutput)
def replace_task(task_id: int, data: TaskInput, uid: int = Depends(current_user)):
    changed = update_task(uid, task_id, data.title, data.priority, data.due_date.isoformat() if data.due_date else None)
    if not changed:
        raise HTTPException(status_code=404, detail="Task not found")
    return get_task(uid, task_id)

@app.delete("/tasks/{task_id}", status_code=204)
def remove_task(task_id: int, uid: int = Depends(current_user)):
    if not delete_task(uid, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
