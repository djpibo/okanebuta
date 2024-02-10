from typing import List

from pydantic import BaseModel


class CreateToDoResponse(BaseModel):
    id: int
    contents: str
    is_done: bool

    class Config:
        from_attributes = True


class ToDoListSchema(BaseModel):
    todos: List[CreateToDoResponse]
