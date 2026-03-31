import os
import json
import re

from constants import constants
from entity.request_entity import TestCase
from utils import config
from utils.redis_help import RedisHelper
from utils.tool import check_type


def main(case: TestCase, isRequest: bool, **kwargs):
    """

    """
    try:

        if isRequest:
            logger = kwargs['logger']
            # 準備連線 redis
            connectionSettings = case.setting.get('connection_settings', {})
            redis = connectionSettings.get('redis', config.connectionSettings[case.serverName]['redis'])
            host = redis.get('host', None)
            if host is None:
                # 如果沒設定即離開
                return

            keepDict = json.loads(os.environ.get(f'{constants.KEEP_VALUES_KEY}{case.uuid}', '{}'))
            globalKeepDict = json.loads(os.environ.get(constants.GLOBAL_KEEP_VALUES_KEY, '{}'))

            port = redis.get('port', 6379)
            password = redis.get('password', None)

            redisHelper = RedisHelper(host, port, password)

            redisGet = redis.get('get')
            if redisGet:
                redisHelper.get_value(redisGet)

            redisSet = redis.get('set')
            if redisSet:
                redisHelper.set_value(redisSet, redisSet)

            # settingRedis = case.setting.get('redis', {})
            # redisDelete = check_type(settingRedis, 'del', list, [], case.pathName)
            # [redisHelper.delete(re.sub(r"{{" + key + "}}", str(value), killKey))
            #  for killKey in redisDelete
            #  for dictionary in [globalKeepDict, keepDict]
            #  for key, value in dictionary.items()]

            settingRedis = case.setting.get('redis', {})
            redisDelete = check_type(settingRedis, 'del', list, [], case.pathName)
            for dictionary in [globalKeepDict, keepDict]:
                for key, value in dictionary.items():
                    redisDelete = [re.sub(r"{{" + key + "}}", str(value), rkey) for rkey in redisDelete]

            logger.info(f'redis_command 將 {redisDelete} 刪除')
            [redisHelper.delete(key) for key in redisDelete]

        return

    except Exception as e:
        case.message.append('redis_command event 錯誤：' + str(e))
