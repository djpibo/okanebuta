from sqlalchemy.orm import declarative_base
from sqlalchemy import Boolean, Column, Integer, String

from request import CreateToDoRequest

Base = declarative_base()


class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done}"

    @classmethod
    def create(cls, request: CreateToDoRequest) -> "ToDo":
        return cls(
            contents=request.contents,
            is_done=request.is_done,
        )

    # done 메소드를 여러 군데서 반복해서 사용한다면 따로 메소드를 빼놓는 것이 효율적
    def done(self) -> "ToDo":
        self.is_done = True
        return self

    def undone(self) -> "ToDo":
        self.is_done = False
        return self
