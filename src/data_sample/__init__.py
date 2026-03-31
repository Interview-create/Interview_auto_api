import importlib
import os
import sys

from entity.request_entity import TestCase


def run_event(case: TestCase, isRequest):
    # 獲取當前模塊所在的目錄
    module_dir = os.path.dirname(__file__)

    # 將目錄添加到系統搜索路徑中
    sys.path.insert(0, module_dir)

    # 執行 event
    event = case.events
    for functionName in event:
        # 使用 importlib.import_module 加載模塊
        function_module = importlib.import_module(functionName)
        function = getattr(function_module, 'main')
        function(case, isRequest)
