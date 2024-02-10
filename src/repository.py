from typing import List

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from connection import get_db
from orm import ToDo


class ToDoRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    # 다건 조회
    def get_todos(self) -> List[ToDo]:
        return list(self.session.scalars(select(ToDo)))

    # 단일 조회
    def get_todo_by_todo_id(self, todo_id: int) -> ToDo | None:
        return self.session.scalar(select(ToDo).where(ToDo.id == todo_id))

    # JPA Entity 유사
    def create_todo(self, todo: ToDo) -> ToDo:
        self.session.add(instance=todo)
        self.session.commit()  # db insert
        self.session.refresh(instance=todo)  # result reload
        return todo

    def update_todo(self, todo: ToDo) -> ToDo:
        self.session.add(instance=todo)
        self.session.commit()  # db update
        self.session.refresh(instance=todo)  # result reload
        return todo

    def delete_todo(self, todo_id: int) -> None:
        self.session.execute(delete(ToDo).where(ToDo.id == todo_id))
        self.session.commit()
