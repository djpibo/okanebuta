from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey

from schema.request import CreateToDoRequest

Base = declarative_base()


class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    # use for clean express
    def __repr__(self):
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done}"

    @classmethod
    def create(cls, request: CreateToDoRequest) -> "ToDo":
        return cls(
            contents=request.contents,
            is_done=request.is_done,
        )

    # being more efficiently when having used same method at many points
    def done(self) -> "ToDo":
        self.is_done = True
        return self

    def undone(self) -> "ToDo":
        self.is_done = False
        return self


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
    todos = relationship("ToDo", lazy="joined")
    # using orm, fetch with argument table when fetching table "user"
    # those clause uses eager loading with left outer join (left side is table "user")
    # lazy="joined" is eager loading, to activate lazy loading use lazy="select", but it might occur 1+N problem

    @classmethod
    def create(cls, username: str, hashed_password: str) -> "User":
        return cls(
            username=username,
            password=hashed_password
        )
