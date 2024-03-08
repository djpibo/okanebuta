from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, DECIMAL

from schema.request import CreateToDoRequest

Base = declarative_base()


class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # use for clean express
    def __repr__(self):
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done}"

    @classmethod
    def create(cls, request: CreateToDoRequest) -> "ToDo":
        return cls(
            contents=request.contents,
            is_done=request.is_done,
            user_id=request.user_id
        )

    # being more efficiently when having used same method at many points
    def done(self) -> "ToDo":
        self.is_done = True
        return self

    def undone(self) -> "ToDo":
        self.is_done = False
        return self


class User(Base):
    __tablename__ = "users"

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


class RateSpec(Base):
    __tablename__ = "exchange_rates_spec"

    id = Column(Integer, primary_key=True, index=True)
    authkey = Column(String(256), nullable=False)
    last_updated = Column(DateTime, nullable=False)


class RateData(Base):
    __tablename__ = "exchange_rates_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    result = Column(Integer)
    cur_unit = Column(String(20))
    ttb = Column(DECIMAL(10, 2))  # 전신환(송금) 받으실 때
    tts = Column(DECIMAL(10, 2))  # 전신환(송금) 보내실 때
    deal_bas_r = Column(DECIMAL(10, 2))  # 매매 기준율
    cur_nm = Column(String(50))

    @classmethod
    def create(cls, result, cur_unit, ttb, tts, deal_bas_r, cur_nm
               ) -> "RateData":
        return cls(
            result=result,
            cur_unit=cur_unit,
            ttb=ttb,
            tts=tts,
            deal_bas_r=deal_bas_r,
            cur_nm=cur_nm
        )


class RateNow(Base):
    __tablename__ = "exchange_rates_now"

    cur_unit = Column(String(20), primary_key=True)
    ttb = Column(DECIMAL(10, 2))  # 전신환(송금) 받으실 때
    tts = Column(DECIMAL(10, 2))  # 전신환(송금) 보내실 때
    deal_bas_r = Column(DECIMAL(10, 2))  # 매매 기준율
    cur_nm = Column(String(50))

    @classmethod
    def create(cls, cur_unit, ttb, tts, deal_bas_r, cur_nm
               ) -> "RateData":
        return cls(
            cur_unit=cur_unit,
            ttb=ttb,
            tts=tts,
            deal_bas_r=deal_bas_r,
            cur_nm=cur_nm
        )
