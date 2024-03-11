import json
from typing import List

from fastapi import Depends
from sqlalchemy import select, delete, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.orm import Session

from database.connection import get_db
from database.orm import ToDo, User, RateSpec, RateData, RateNow


class ToDoRepository:
    def __init__(self, session: Session = Depends(get_db)):  # constructor DI (Session)
        self.session = session

    # multiple fetch
    def get_todos(self) -> List[ToDo]:
        return list(self.session.scalars(select(ToDo)))

    # single fetch
    def get_todo_by_todo_id(self, todo_id: int) -> ToDo | None:  # return nullable object
        # return self.session.scalar(select(ToDo).where(ToDo.id == todo_id))
        return self.session.execute(select(ToDo).where(ToDo.id == todo_id)).scalar()

    # Like JPA Entity, don't need to use insert query

    def create_todo(self, todo: ToDo) -> ToDo:
        # self.session.begin()  # for autocommit = True
        self.session.add(instance=todo)
        # self.session.merge(instance=todo)
        # self.session.flush()
        self.session.commit()  # db insert, even though autocommit is True should invoke commit()
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
        # try:
        #     query = "SELECT * FROM users WHERE username = 'mine'"
        #     return self.session.execute(query).scalar()
        #     # return self.session.scalar(select([User]).hint("STRAIGHT_JOIN").where(User.c.username == username))
        # except AttributeError:
        return self.session.scalar(select(User).where(User.username == username))

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()  # db update
        self.session.refresh(instance=user)  # result reload
        return user


class RateRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_authkey(self) -> str | None:
        return self.session.query(RateSpec).order_by(RateSpec.last_updated.desc()).first().authkey

    def get_rate_data(self, cur_unit: str) -> RateNow | None:
        return self.session.execute(select(RateNow).where(RateNow.cur_unit == cur_unit)).scalar()

    def save_rate_data(self, new_data: RateData) -> RateData | None:
        self.session.add(instance=new_data)
        self.session.commit()
        return new_data

    def save_rate_now(self, rate_now: RateNow):
        self.session.merge(instance=rate_now)
        self.session.commit()

    def save_transactions(self, cur_unit: str, ttb: str, tts: str, deal_bas_r: str, cur_nm: str):
        cur_data = RateNow.create(cur_unit=cur_unit, ttb=ttb, tts=tts, deal_bas_r=deal_bas_r, cur_nm=cur_nm)
        self.session.merge(instance=cur_data)
        self.session.commit()
