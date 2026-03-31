from datetime import datetime
from entity.request_entity import TestCase


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將請求資料中的 平假日房價 替換成新的 值。
    參數:
        payload (json): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    logger = kwargs['logger']
    try:

        if not isRequest:
            return

        weekday = datetime.today().isoweekday()
        if weekday in (1, 2, 3, 7):
            case.payload['booking'][0]['origin_price'] = 40000
            case.payload['booking'][0]['origin_point'] = 40000
            case.payload['booking'][0]['pay_price'] = 40000
            case.payload['booking'][0]['pay_point'] = 40000
        elif weekday in (5, ):
            case.payload['booking'][0]['origin_weekend_point'] = 40000
            case.payload['booking'][0]['origin_weekend_price'] = 40000
            case.payload['booking'][0]['pay_weekend_point'] = 40000
            case.payload['booking'][0]['pay_weekend_price'] = 40000
        elif weekday in (4, 6):
            case.payload['booking'][0]['origin_price'] = 20000
            case.payload['booking'][0]['origin_point'] = 20000
            case.payload['booking'][0]['pay_price'] = 20000
            case.payload['booking'][0]['pay_point'] = 20000
            case.payload['booking'][0]['origin_weekend_point'] = 20000
            case.payload['booking'][0]['origin_weekend_price'] = 20000
            case.payload['booking'][0]['pay_weekend_point'] = 20000
            case.payload['booking'][0]['pay_weekend_price'] = 20000

    except Exception as e:
        logger.info(f'房價替換有錯,err：' + str(e))
        case.message.append(f'房價替換有錯, err：' + str(e))
