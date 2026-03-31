import asyncio
import sys
import os

from core.TestPlanTool import TestPlanTool
from utils import config


async def test_main():
    # 取得命令列參數, 從 docker 來，或者直接 run 時給的
    # docker run -e ARGS="data/plan data/plan data/plan" automation
    # pyhon3 main.py data/plan data/plan data/plan

    args = [] + os.environ.get("ARGS", "").split() + sys.argv[1:]
    # args = ['data_sample/plan'] + os.environ.get("ARGS", "").split() + sys.argv[1:]
    # args = ['data/plan/P1_存取款_一般存取款'] + os.environ.get("ARGS", "").split() + sys.argv[1:]
    args.extend(config.planName)

    # 如果沒有參數，則輸出提示並退出
    if len(args) == 0:
        print("請輸入參數")
        sys.exit()

    testPlanTool = TestPlanTool()
    await testPlanTool.run_test_plan_summary_list(args)


asyncio.run(test_main())
