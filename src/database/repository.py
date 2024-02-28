from typing import List

from fastapi import Depends
from sqlalchemy import select, delete, create_engine, MetaData, Table, Column, Integer, String, Boolean
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
        self.session.begin()  # for autocommit = True
        self.session.add(instance=todo)
        # self.session.merge(instance=todo)
        # self.session.flush()
        self.session.commit()  # db insert
        # self.session.refresh(instance=todo)  # result reload

        return todo

    def update_todo(self, todo: ToDo) -> ToDo:
        # self.session.begin()  # for autocommit = True
        self.session.add(instance=todo)
        # self.session.flush()
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


class NewRepository:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData(bind=self.engine)
        self.users = Table('todos', self.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('contents', String),
                           Column('is_done', Boolean),
                           Column('user_id', Integer))
        self.metadata.create_all()

    def create_user(self, todo: ToDo):
        query = self.users.insert().values(id=100, content=todo.contents, is_done=todo.is_done, user_id=todo.user_id)
        with self.engine.connect() as conn:
            conn.execute(query)

    def get_user_by_id(self, user_id):
        query = self.users.select().where(self.users.c.id == user_id)
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return result.fetchone()

    def get_all_users(self):
        query = self.users.select()
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return result.fetchall()

    def update_user(self, user_id, content, is_done):
        query = self.users.update().where(self.users.c.id == user_id).values(content=content, is_done=is_done)
        with self.engine.connect() as conn:
            conn.execute(query)

    def delete_user(self, user_id):
        query = self.users.delete().where(self.users.c.id == user_id)
        with self.engine.connect() as conn:
            conn.execute(query)
