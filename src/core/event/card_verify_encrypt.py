from constants import constants
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from datetime import datetime
from entity.request_entity import TestCase
import json
import os
import random


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將拍卡請求資料中的 key 替換成新的 值,只有帳房會用到。
    參數:
        payload (json): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    try:

        if not isRequest:
            return

        keepValuesKey = f'{constants.KEEP_VALUES_KEY}{case.uuid}'
        keepDict = json.loads(os.environ.get(keepValuesKey, '{}'))

        key = b'55bc84ab6bac04601f97be0e'
        cardID = case.setting.get('cardID', [])
        uuidKey = case.setting.get('uuidKey', [])
        iat = str(int(datetime.now().timestamp()))
        new_uuid = keepDict.get(uuidKey, '')

        data_to_encrypt = '{{ "id": "{}", "form_data_uuid": "{}", "iat": {} }}'.format(
            cardID, new_uuid, iat)
        data_to_encrypt = data_to_encrypt.encode('utf-8')

        # 使用Triple DES算法和ECB模式创建Cipher对象
        cipher = Cipher(algorithms.TripleDES(
            key), modes.ECB(), backend=default_backend())

        # 创建加密器
        encryptor = cipher.encryptor()

        # 將數據填充為區塊大小的倍數
        data_to_encrypt = data_to_encrypt + \
            b'\x01' * (8 - (len(data_to_encrypt) % 8))

        # 加密数据
        encrypted_data = encryptor.update(
            data_to_encrypt) + encryptor.finalize()

        # 将加密后的数据转换为十六进制字符串
        hex_string = encrypted_data.hex()

        # 生成一个随机整数 i，范围为 [0, len(hex_string))
        i = random.randint(0, len(hex_string))

        # 使用字符串切片获取前缀和后缀
        suffix = hex_string[:i]
        prefix = hex_string[i:]

        # 构建最终密码
        password = suffix + '©' + prefix

       # 如果payload不是這階層就要調整內容
        case.payload['key'] = password

    except Exception as e:
        case.message.append('card_verify_encrypt event 錯誤' + str(e))
