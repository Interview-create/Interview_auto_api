# -*- coding: utf-8 -*-
import os
from core.TestPlanSummaryJson import TestPlanSummaryJson
from utils.tool import split_last_slash


def init():
    # 獲取當前目錄的絕對路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 使用 os.listdir() 取得資料夾中所有檔案清單
    for root, dirs, files in os.walk(current_dir):
        for file in sorted(files):
            # 確保只處理 JSON 檔案
            if file.endswith("task.json"):
                # 獲取相對路徑
                relative_path = os.path.relpath(root, current_dir)
                path, path2 = split_last_slash(current_dir)
                name = relative_path.split('/', 1)
                path2 = os.path.join(path2, name[0])
                testPlanSummaryJson = TestPlanSummaryJson()
                testPlanSummaryJson.get_task(path2, name[1], 0, '')
