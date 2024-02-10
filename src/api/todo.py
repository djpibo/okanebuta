from fastapi import Body, HTTPException, Depends, APIRouter
from pydantic import BaseModel
from orm import ToDo
from repository import ToDoRepository
from request import CreateToDoRequest
from response import CreateToDoResponse

router = APIRouter(prefix="/todos")


@router.get("/{todo_id}", status_code=200)
def get_todo_handler(
        todo_id: int,
        # session: Session, # Replaced by Repository Pattern
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> CreateToDoResponse:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo:
        return CreateToDoResponse.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found!")


class CreateTodoRequest(BaseModel):
    id: int
    contents: str
    id_done: bool


@router.post("", status_code=201)
def create_todo_handler(
        request: CreateToDoRequest,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
) -> CreateToDoResponse:
    todo: ToDo = ToDo.create(request=request)
    todo: ToDo = todo_repo.create_todo(todo=todo)

    return CreateToDoResponse.from_orm(todo)


@router.patch("/{todo_id}")
def update_todo_handler(
        todo_id: int,
        is_done: bool = Body(..., embed=True),
        todo_repo: ToDoRepository = Depends(ToDoRepository)
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo:
        todo.is_done if is_done else todo.undone()  # 삼항 연산자
        todo: ToDo = todo_repo.update_todo(todo=todo)
        return CreateToDoResponse.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found!")


@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
        todo_id: int,
        todo_repo: ToDoRepository = Depends(ToDoRepository)
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo Not Found!")

    todo_repo.delete_todo(todo_id=todo_id)
