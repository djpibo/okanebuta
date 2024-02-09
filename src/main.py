from typing import List
from fastapi import FastAPI, Body, HTTPException, Depends
from pydantic import BaseModel
from requests import session
from sqlalchemy.orm import Session
from connection import get_db
from orm import ToDo
from repository import get_todos, get_todo_by_todo_id, create_todo, update_todo, delete_todo
from request import CreateToDoRequest
from response import ToDoListSchema, CreateToDoResponse

app = FastAPI()


@app.get("/")
def health_check_handler():
    return {"ping": "pong"}


@app.get("/todos", status_code=200)  # 전체조회와 같은 복수형은 s를 붙인다고 함
def get_todo_handler(
        order: str | None = None,
        session: Session = Depends(get_db),
) -> ToDoListSchema:
    todos: List[ToDo] = get_todos(session=session)
    if order and order == "DESC":
        return ToDoListSchema(
            todos=[CreateToDoResponse.from_orm(todo) for todo in todos[::-1]]
        )
    return ToDoListSchema(
        todos=[CreateToDoResponse.from_orm(todo) for todo in todos]
    )


@app.get("/todos/{todo_id}", status_code=200)
def get_todo_handler(
        todo_id: int,
        session: Session = Depends(get_db)
) -> CreateToDoResponse:
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if todo:
        return CreateToDoResponse.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found!")


class CreateTodoRequest(BaseModel):
    id: int
    contents: str
    id_done: bool


@app.post("/todos", status_code=201)
def create_todo_handler(
        request: CreateToDoRequest,
        session: Session = Depends(get_db),
) -> CreateToDoResponse:
    todo: ToDo = ToDo.create(request=request)
    todo: ToDo = create_todo(session=session, todo=todo)

    return CreateToDoResponse.from_orm(todo)


@app.patch("/todos/{todo_id}")
def update_todo_handler(
        todo_id: int,
        is_done: bool = Body(..., embed=True),
        session: Session = Depends(get_db)
):
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if todo:
        todo.is_done if is_done else todo.undone()  # 삼항 연산자
        todo: ToDo = update_todo(session=session, todo=todo)
        return CreateToDoResponse.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found!")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo_handler(
        todo_id: int,
        session: Session = Depends(get_db)
):
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo Not Found!")

    delete_todo(session=session, todo_id=todo_id)
