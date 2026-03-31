import importlib
import os
import sys

from entity.request_entity import TestCase


def run_request_event(case: TestCase, logger):
    run_event(case, True, logger)


def run_response_event(case: TestCase, logger):
    run_event(case, False, logger)


def run_event(case: TestCase, isRequest, logger):
    # 獲取當前模塊所在的目錄
    module_dir = os.path.dirname(__file__)

    # 將目錄添加到系統搜索路徑中
    sys.path.insert(0, module_dir)

    # 執行 event
    events = case.requestEvents if isRequest else case.responseEvents
    for functionName in events:
        try:
            # 使用 importlib.import_module 加載模塊
            function_module = importlib.import_module(functionName)
            function = getattr(function_module, 'main')
            function(case, isRequest, logger=logger)
        except ModuleNotFoundError:
            # 當模塊不存在時的錯誤處理
            raise f"events 模塊 {functionName} 不存在, 或者你少指定了模塊名稱，執行 pipenv install -r requirements.txt"
        except AttributeError:
            # 當函數不存在時的錯誤處理
            # print(f"events 函數 {functionName}.main 不存在")
            pass
        except Exception as e:
            case.message.append(f'events 模塊 {functionName} 出了點問題：' + str(e))
