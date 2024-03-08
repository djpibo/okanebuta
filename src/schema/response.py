from dataclasses import dataclass
from decimal import Decimal
from typing import List
from marshmallow import fields
from pydantic import BaseModel


class ToDoSchema(BaseModel):
    id: int
    contents: str
    is_done: bool
    user_id: int

    class Config:
        from_attributes = True


class ToDoListSchema(BaseModel):
    todos: List[ToDoSchema]


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class JWTResponse(BaseModel):
    access_token: str


class RateDataSchema(BaseModel):
    result: int
    cur_unit: str
    ttb: Decimal
    tts: Decimal
    deal_bas_r: Decimal
    # bkpr: str
    # yy_efee_r: str
    # ten_dd_efee_r: str
    # kftc_bkpr: str
    # kftc_deal_bas_r: str
    cur_nm: str

    class Config:
        from_attributes = True


class ExchangeResponse(BaseModel):
    cur_unit: str
    cur_nm: str
    pay_money: str
    receive_money: str
    tts: str
    fee: str

    class Config:
        from_attributes = True
