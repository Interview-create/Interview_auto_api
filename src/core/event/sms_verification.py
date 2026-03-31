import json
import os

from constants import constants
from entity.request_entity import TestCase
from jsonpath_ng import parse
from utils import config
from utils.redis_help import RedisHelper


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將請求資料中的 hash 替換成新的 值。
    參數:
        payload (json): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    logger = kwargs['logger']
    key = ''
    try:

        if isRequest:
            return

        try:
            responseJson = case.response.json()
        except json.decoder.JSONDecodeError:
            return

        keepValuesKey = f'{constants.KEEP_VALUES_KEY}{case.uuid}'
        keepDict = json.loads(os.environ.get(keepValuesKey, '{}'))

        # identifyCode = responseJson.get('identifyCode', '')
        # message = responseJson.get('message', None) or identifyCode

        messageKey = case.setting.get('sms_message_key', 'message')
        path = parse(messageKey)
        match = path.find(responseJson)
        if not match:
            case.message.append(f'responseJson 中找不到 {messageKey}')
            return
        message = match[0].value
        if message:
            # 準備連線 redis
            connectionSettings = case.setting.get('connection_settings', {})
            redis = connectionSettings.get('redis', config.connectionSettings[case.serverName]['redis'])
            redis_host = redis.get('host', 'localhost')
            redis_port = redis.get('port', 6379)
            redis_password = redis.get('password', None)

            redis_helper = RedisHelper(redis_host, redis_port, redis_password)

            keepKey = case.setting.get('sms_verification_key', 'ars_USER_ID_num')

            userId = keepDict.get(keepKey, None)
            if userId is None:
                case.message.append(f'sms_verification_key 或 ars_USER_ID_num 未設定')
                return
            key = f'ARS-security-check-{int(userId)}-{message}'

            keepDict["identify_code"] = message
            verifyCode = redis_helper.get_value(key)[4:]
            logger.info(f'redis_command 取得 {key} 值為 {verifyCode}')
            keepDict["verify_code"] = str(verifyCode, encoding='utf-8')
            os.environ[keepValuesKey] = json.dumps(keepDict)

    except Exception as e:
        logger.info(f'短信驗證 錯誤 key: {key}, err：' + str(e))
        case.message.append(f'短信驗證 錯誤 key: {key}, err：' + str(e))
