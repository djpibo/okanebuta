from fastapi import Depends

from database.orm import RateNow, RateData
from database.repository import RateRepository


class RateService:

    @staticmethod
    def save_rate(rate_repo: RateRepository = Depends()):
        cur_data = RateNow.create(
            cur_unit=data['cur_unit'],
            ttb=data['ttb'],
            tts=data['tts'],
            deal_bas_r=data['deal_bas_r'],
            cur_nm=data['cur_nm'])
        rate_repo.save_rate_now(cur_data)

        insert_data = RateData.create(
            result=data['result'],
            cur_unit=data['cur_unit'],
            ttb=data['ttb'],
            tts=data['tts'],
            deal_bas_r=data['deal_bas_r'],
            cur_nm=data['cur_nm'])
        rate_repo.save_rate_data(insert_data)
        rate_repo.save_rate_now(cur_data)
        # rate_repo.save_transactions()
