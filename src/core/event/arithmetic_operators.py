import json
import os

from jinja2 import Template
from jsonpath_ng import parse

from constants import constants
from entity.request_entity import TestCase

functionName = 'arithmetic_operators'


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    處理數字運算
    :param case:
    :param isRequest:
    Args:
        case:
        isRequest:
        logger:
        **kwargs:

    Returns:

    """
    try:
        setting = case.setting

        # 取得需要被替換的 key
        arithmeticOperatorsKeys = setting.get(f'{functionName}_keys', [])

        # 沒有即返回
        if not arithmeticOperatorsKeys:
            return

        logger = kwargs['logger']
        # 處理 keep payload, headers value, expected
        keepDict = json.loads(os.environ.get(
            f'{constants.KEEP_VALUES_KEY}{case.uuid}', '{}'))
        if isRequest:
            process_arithmetic_operators(
                case.payload, arithmeticOperatorsKeys, keepDict, logger, 'payload')
        else:
            process_arithmetic_operators(
                case.expected.response, arithmeticOperatorsKeys, keepDict, logger, 'expected.response')

    except Exception as e:
        case.message.append(f'{functionName} event 錯誤：' + str(e))


def update_json_node(jsonData, jsonPath, newValue):
    """
    修改 JSON 物件中指定 JSONPath 表達式的節點值

    """
    # 定義要修改的 JSONPath 表達式
    path_to_update = parse(jsonPath)

    # 使用 jsonpath_ng 找到對應的節點
    matches = [match for match in path_to_update.find(jsonData)]

    # 修改節點的值
    if matches:
        for match in matches:
            update_value(jsonData, str(match.full_path), newValue)
    else:
        raise Exception(f"在 需要上傳的檔案，找不到指定的 JSONPath：{jsonPath}")


def update_value(jsonData, path, newValue):
    # 將 JSONPath 路徑字串拆分為路徑段落
    paths = path.split('.')

    # 取得目標節點所在的 JSON 物件
    current = jsonData

    # 迭代路徑段落，找到目標節點的父節點
    for p in paths[:-1]:
        # 判斷路徑段落是否是數字，如果是數字，則轉換為整數型態
        p = p.strip('[]')
        if p.isdigit():
            p = int(p)

        # 取得父節點
        current = current[p]

    # 取得目標節點的名稱
    last = paths[-1].strip('[]')

    # 如果目標節點名稱是數字，則轉換為整數型態
    if last.isdigit():
        last = int(last)

    # 修改目標節點的值
    current[last] = newValue


def process_arithmetic_operators(target, arithmeticOperatorsKeys, keepDict, logger, targetName):
    for key in arithmeticOperatorsKeys:
        try:
            path = parse(key)
            match = path.find(target)
            if match:
                matchedValue = match[0].value
                if isinstance(matchedValue, int):
                    continue

                # 編譯模板
                template = Template(matchedValue)

                for k, v in keepDict.items():
                    try:
                        keepDict[k] = int(v)
                    except:
                        pass

                # 渲染模板
                result_str = template.render(keepDict)

                logger.info(
                    f'{functionName} 將 {targetName}.{key} 的值 {matchedValue} 替換為 {result_str}')

                update_json_node(target, key, float(result_str))
            else:
                logger.info(f'{functionName} {targetName}.{key} 找不到')
        except Exception as e:
            logger.error(
                f'{functionName} event 替換 {targetName}.{key} 時 錯誤：{e}')
