import json
from datetime import datetime
from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException

from database.orm import RateNow, RateData
from database.repository import RateRepository
from redis_cache import redis_client

import requests

from schema.request import ExchangeMoneyRequest
from schema.response import ExchangeResponse
from service.rate import RateService

router = APIRouter(prefix="/rates")


@router.get("/peek", status_code=200)
def rates_peek_handler(
        rate_repo: RateRepository = Depends(),
        rate_srvc: RateService = Depends()
):
    authkey = redis_client.get("authkey")
    if not authkey:
        authkey = rate_repo.get_authkey()
        redis_client.set("authkey", authkey)

    try:
        response = requests.get(f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?"
                                f"authkey={authkey}&searchdate={datetime.now().strftime("%Y%m%d")}&data=AP01")
        response.raise_for_status()  # 요청이 실패하면 예외 발생
        data = response.json()
        if not data:
            raise HTTPException(status_code=500, detail="No Rate Data")  # 데이터 없음
        for item in data:
            if item['cur_unit'] == 'JPY(100)':
                data = item
                print(data)
                # rate_srvc.save_rate(data)
                x = json.loads(data)
        # return RateDataSchema.from_orm(data)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="External API request failed")  # 예외 처리


@router.post("/exchange", status_code=200)
def rates_exchange_handler(
        request: ExchangeMoneyRequest,
        rate_repo: RateRepository = Depends()
):
    rateNow: RateNow = rate_repo.get_rate_data(request.cur_unit)
    resp: ExchangeResponse(
        cur_nm=rateNow.cur_nm,
        cur_unit=rateNow.cur_unit,
        pay_money=format(request.money, ','),
        receive_money=format(rateNow.deal_bas_r * request.money, ','),
        tts=format(rateNow.tts, ',.2f'),
        fee=format(rateNow.deal_bas_r * request.money / 10, ',')
        )
