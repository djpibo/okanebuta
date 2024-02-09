from typing import List

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from orm import ToDo


# 다건 조회
def get_todos(session: Session) -> List[ToDo]:
    return list(session.scalars(select(ToDo)))


# 단일 조회
def get_todo_by_todo_id(session: Session, todo_id: int) -> ToDo | None:
    return session.scalar(select(ToDo).where(ToDo.id == todo_id))


# JPA Entity 유사
def create_todo(session: Session, todo: ToDo) -> ToDo:
    session.add(instance=todo)
    session.commit()  # db insert
    session.refresh(instance=todo)  # result reload
    return todo


def update_todo(session: Session, todo: ToDo) -> ToDo:
    session.add(instance=todo)
    session.commit()  # db update
    session.refresh(instance=todo)  # result reload
    return todo


def delete_todo(session: Session, todo_id: int) -> None:
    session.execute(delete(ToDo).where(ToDo.id == todo_id))
    session.commit()
