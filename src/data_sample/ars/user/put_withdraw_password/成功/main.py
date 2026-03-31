# -*- coding: utf-8 -*-
import asyncio
import os

from core.TestPlanTool import TestPlanTool


async def init():
    # 獲取當前目錄的絕對路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 使用 os.listdir() 取得資料夾中所有檔案清單
    for root, dirs, files in os.walk(current_dir):
        for file in sorted(files):
            # 確保只處理 JSON 檔案
            if file.endswith("task.json"):
                # 獲取相對路徑
                path = root.split('/')[-4:]
                path2 = os.path.join(path[0], path[1])
                path3 = os.path.join(path[2], path[3])
                testPlanTool = TestPlanTool()
                await testPlanTool.run_task(path2, path3)

asyncio.run(init())
