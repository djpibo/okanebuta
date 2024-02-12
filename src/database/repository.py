from typing import List

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.connection import get_db
from database.orm import ToDo, User


class ToDoRepository:
    def __init__(self, session: Session = Depends(get_db)):  # constructor DI (Session)
        self.session = session

    # multiple fetch
    def get_todos(self) -> List[ToDo]:
        return list(self.session.scalars(select(ToDo)))

    # single fetch
    def get_todo_by_todo_id(self, todo_id: int) -> ToDo | None:  # return nullable object
        return self.session.scalar(select(ToDo).where(ToDo.id == todo_id))

    # Like JPA Entity, don't need to use insert query
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


class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.username == username)
        )

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()  # db update
        self.session.refresh(instance=user)  # result reload
        return user
