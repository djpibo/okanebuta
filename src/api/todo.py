from typing import List

from fastapi import HTTPException, Depends, APIRouter, Body
from pydantic import BaseModel

from database.orm import ToDo, User
from database.repository import ToDoRepository, UserRepository, NewRepository
from schema.request import CreateToDoRequest
from schema.response import ToDoSchema, ToDoListSchema
from security import get_access_token
from service.user import UserService

router = APIRouter(prefix="/todos")


@router.get("", status_code=200)
def get_todos_handler(
        # session: Session, # Replaced by Repository Pattern
        # todo_repo: ToDoRepository = Depends(), # Replaced by UserService function
        access_token: str = Depends(get_access_token),
        order: str | None = None,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
) -> ToDoListSchema:
    username: str = user_service.decode_jwt(access_token=access_token)
    user: User | None = user_repo.get_user_by_username(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    # todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    todos: List[ToDo] = user.todos  # fetch through eager loading when user_repo method called
    if order and order == "DESC":
        return ToDoListSchema(
            todos=[ToDoSchema.from_orm(todo) for todo in todos[::-1]]
        )
    return ToDoListSchema(
        todos=[ToDoSchema.from_orm(todo) for todo in todos]
    )


@router.get("/{todo_id}", status_code=200)
def get_todo_handler(
        todo_id: int,
        todo_repo: ToDoRepository = Depends(),
) -> ToDoSchema:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo:
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")


@router.get("/{todo_id}", status_code=200)
def get_todo_handler(
        todo_id: int,
        # session: Session, # Replaced by Repository Pattern
        # todo_repo: ToDoRepository = Depends(), # Replaced by UserService function
        user_repo: UserRepository = Depends(),
        user_service: UserService = Depends(),
        access_token: str = Depends(get_access_token)
) -> ToDoSchema:
    username: str = user_service.decode_jwt(access_token=access_token)
    user: User | None = user_repo.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found!")

    # todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    todo: List[ToDo] | None = user.todos  # fetch through eager loading when user_repo method called
    if todo:
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found!")


class CreateTodoRequest(BaseModel):
    id: int
    contents: str
    id_done: bool


@router.post("/", status_code=201)
def create_todo_handler(
        request: CreateToDoRequest,
        todo_repo: ToDoRepository = Depends()
):
    todo: ToDo = ToDo.create(request=request)
    todo: ToDo = todo_repo.create_todo(todo=todo)
    # print(todo.id)
    return ToDoSchema.from_orm(todo)


@router.patch("/{todo_id}")
def update_todo_handler(
        todo_id: int,
        is_done: bool = Body(..., embed=True),
        todo_repo: ToDoRepository = Depends()
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo:
        todo.done() if is_done else todo.undone()  # 삼항 연산자
        todo.user_id = 1
        todo: ToDo = todo_repo.update_todo(todo=todo)
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found!")


@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
        todo_id: int,
        todo_repo: ToDoRepository = Depends()
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo Not Found!")

    todo_repo.delete_todo(todo_id=todo_id)
