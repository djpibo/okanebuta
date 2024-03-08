from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CreateToDoRequest(BaseModel):
    contents: str
    is_done: bool
    user_id: int


class SignUpRequest(BaseModel):
    username: str
    password: str


class LogInRequest(BaseModel):
    username: str
    password: str


class CreateOTPRequest(BaseModel):
    email: str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: int


class ExchangeMoneyRequest(BaseModel):
    money: Decimal
    cur_unit: str
