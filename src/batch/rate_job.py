import asyncio
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
import requests

from fastapi import Depends, HTTPException

from database.orm import RateNow
from database.repository import RateRepository
from redis_cache import redis_client


def my_batch_job(
        rate_repo: RateRepository = Depends()
):
    print("배치 작업이 실행됨")
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
                print(type(data['cur_unit']), type(data['ttb']), type(data['tts']), type(data['deal_bas_r']),
                      type(data['cur_nm']), type(data['result']))  # 출력: <class 'str'>

                cur_data = RateNow.create(
                    cur_unit=data['cur_unit'],
                    ttb=data['ttb'],
                    tts=data['tts'],
                    deal_bas_r=data['deal_bas_r'],
                    cur_nm=data['cur_nm'])
                rate_repo.save_rate_now(cur_data)
                # data = rate_repo.save_rate(data['result'], data['cur_unit'], data['ttb'], data['tts'],
                #                           data['deal_bas_r'], data['cur_nm'])
        # return RateDataSchema.from_orm(data)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="External API request failed")  # 예외 처리


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(my_batch_job, 'interval', seconds=15)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
