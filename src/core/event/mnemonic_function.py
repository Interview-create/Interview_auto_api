from constants import constants
from entity.request_entity import TestCase

import json
import os


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    將請求資料中的 助記詞問題跟答案 替換成新的 值。
    參數:
        payload (json): 原始請求資料。
    回傳:
        dict: 將 {{}} 替換成新的 值 後的請求資料。
    """
    logger = kwargs['logger']
    try:

        if isRequest:
            return

        keepValuesKey = f'{constants.KEEP_VALUES_KEY}{case.uuid}'
        keepDict = json.loads(os.environ.get(keepValuesKey, '{}'))

        mnemonic = case.setting.get('mnemonic_key', 'mnemonic_sample')

        keepDict["mnemonic_answer_position_0"] = keepDict['mnemonic_question'][0]
        keepDict["mnemonic_answer_position_1"] = keepDict['mnemonic_question'][1]
        keepDict["mnemonic_answer_position_2"] = keepDict['mnemonic_question'][2]
        keepDict["mnemonic_answer_position_3"] = keepDict['mnemonic_question'][3]

        print(keepDict[mnemonic][keepDict['mnemonic_question'][0]-1])
        keepDict["mnemonic_answer_0"] = str(
            keepDict[mnemonic][keepDict['mnemonic_question'][0]-1])
        keepDict["mnemonic_answer_1"] = str(
            keepDict[mnemonic][keepDict['mnemonic_question'][1]-1])
        keepDict["mnemonic_answer_2"] = str(
            keepDict[mnemonic][keepDict['mnemonic_question'][2]-1])
        keepDict["mnemonic_answer_3"] = str(
            keepDict[mnemonic][keepDict['mnemonic_question'][3]-1])

        os.environ[keepValuesKey] = json.dumps(keepDict)

    except Exception as e:
        logger.info(f'助記詞替換有錯,err：' + str(e))
        case.message.append(f'助記詞替換有錯, err：' + str(e))
