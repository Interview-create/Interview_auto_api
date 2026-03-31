from constants import constants
from datetime import datetime
from entity.request_entity import TestCase
from time import sleep

import json
import os
import pyotp


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將請求資料中的 OTP 替換成新的 值。
    參數:
        payload (json): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    logger = kwargs['logger']
    key = ''
    try:

        if not isRequest:
            return

        keepValuesKey = f'{constants.KEEP_VALUES_KEY}{case.uuid}'
        keepDict = json.loads(os.environ.get(keepValuesKey, '{}'))

        otpKey = case.setting.get('otp_key', '')
        if otpKey != 'bank_otp_secret':
            totp = pyotp.TOTP(keepDict[otpKey])
        else:
            totp = pyotp.TOTP('6LBAFA5BWIWWSJYLP6LQUHLIVA3JUTOO')

        # OTP每30秒更新一次,避免在29-0秒觸發OTP
        if int(datetime.now().timestamp()) % 30 > 28:
            sleep(3)
        # 如果payload不是這階層就要調整內容
        case.payload["security_check"]["verify_code"] = totp.now()

    except Exception as e:
        logger.info(f'OTP驗證 錯誤 key: {key}, err：' + str(e))
        case.message.append(f'OTP驗證 錯誤 key: {key}, err：' + str(e))
