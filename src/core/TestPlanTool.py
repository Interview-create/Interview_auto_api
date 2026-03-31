import asyncio
import datetime
import glob
import json
import os
import threading

import utils
from core.HtmlReport import HtmlReport
from core.TestPlan import TestPlan
from core.Version import Version
from entity.report import ReportEntity, ReportType
from utils import slack_help, config
from utils import tool
from utils.logger import logger

"""
    這裡主要做用是將組好的 json 格式 去發送給 API 請求，並且執行測試，做log 處理，產 html report。
        入口會是這兩個函數，並且會自動找到資料夾下的所有 test開頭 .json結尾的檔案，並按照資料夾名稱排序。
            run_test_plan_summary_list 多個 plan 名稱 ['data/plan/登入測試', 'data/plan/取得版本號']
            run_test_plan_summary 單個 plan 名稱，可以是 'data/plan', 'data/plan/登入測試'
"""


class TestPlanTool:
    def __init__(self):
        self.basePath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.logger = utils.logger.Logger('').logger
        self.startTime: datetime.datetime = tool.get_cst_time()
        self.endTime: datetime.datetime = tool.get_cst_time()
        self.baseReportPath = os.path.join(self.basePath, 'log', self.startTime.strftime("%Y%m%d"))
        self.reportFileName = f'{self.startTime.strftime("%H%M")}-result.html'
        self.statisticsJsonName = f'data-{self.startTime.strftime("%H%M")}.json'
        self.reportPath = os.path.join(self.baseReportPath, self.reportFileName)
        self.statisticsJsonPath = os.path.join(self.baseReportPath, self.statisticsJsonName)
        self.reportList: list[ReportEntity] = []
        self.reportTotalData: dict = {}
        htmlReport = HtmlReport()
        self.baseReportHtml = htmlReport.table_style
        self.versionHtml = ''
        self.statisticsKey = self.startTime.strftime("%m-%d %H:%M")
        self.statistics = {
            self.statisticsKey: {}
        }

    # 初始化，取版號
    async def setup(self):
        """
        初始化，因為init 不能await
        Returns:
        """
        # 取得各 server 的版號, URL, 名稱, 環境
        version = Version(self.logger)
        versionHtml = await version.get_version_html()
        self.versionHtml = versionHtml

    # 單個 plan 入口
    async def run_test_plan_summary(self, summaryName: str):
        assert summaryName, "ERROR run_test_plan_summary 沒有指定測試組名稱"
        return await self.run_test_plan_summary_list([summaryName])

    # 多個 plan 入口
    async def run_test_plan_summary_list(self, summaryNames: list[str]):
        # 判斷是否有參數，如果沒有則輸出提示並退出
        assert summaryNames, "ERROR run_test_plan_summary_list 沒有指定測試組名稱"

        print(f'輸入的planName summaryNames : {summaryNames}')
        print(f'路徑 basePath : {self.basePath}')

        await self.setup()
        slack_help.send(f'本次測試案例開始 開始時間: {self.startTime.strftime("%Y-%m-%d %H:%M:%S")} '
                        f'<{config.reportUrl}/{self.startTime.strftime("%Y%m%d")}/{self.reportFileName}|傳送門>')
        print(f"啟動時間為: {self.startTime.strftime('%Y-%m-%d %H:%M:%S')}")

        # 取得n天內的統計數據
        await self._get_statistics()

        # 組出測試組，找出目錄裡有 test 開頭的 json 檔。如果 summaryName 以 plan 結尾，則搜尋裡面的測試組。
        planNamePath = [f"{planName}/{plan}" for planName in summaryNames if planName.endswith('/plan') for plan in
                        self._find_test_dirs(planName)]
        planNamePath.extend([planName for planName in summaryNames if not planName.endswith('/plan')])

        if len(planNamePath) == 0:
            print("ERROR run_test_plan_summary_list 沒有找到測試組名稱")
            return

        # 取得 queue json 資訊
        queuePath = os.path.join(self.basePath, config.queuePath)
        queueJson = self._get_json(queuePath)
        queueList = queueJson.get('queue', [])

        # 處理 queue 清單
        for item in reversed(queueList):
            if item.get('plans', [])[0] == 'all':
                item['plans'] = planNamePath
                continue
            b = set(item.get('plans', []))
            a = set(planNamePath)
            planNamePath = list(a - b)
            item['plans'] = list(b & a)

        # 開始執行
        for item in queueList:
            queueType = item.get('type', '')
            plans = item.get('plans', [])
            if queueType == 'ST':
                for planName in sorted(plans):
                    testPlan = TestPlan(self.statisticsKey)
                    (reportList, statistics) = await testPlan.run_test_plan(planName)
                    self._set_data(reportList, statistics)
                    # 組報告
                    await self.build_report()
            else:
                print(plans)
                threads = []
                for i in plans:
                    thread = threading.Thread(target=self.run_coroutine, args=(i,))
                    thread.start()
                    threads.append(thread)

                # 等待所有執行緒完成
                for thread in threads:
                    thread.join()

        # 存統計數據
        await self._save_statistics()

        # 組報告
        await self.build_report()

        # 發通知
        await self._send_notification()

    def run_coroutine(self, i):
        testPlan = TestPlan(self.statisticsKey)
        (reportList, statistics) = asyncio.run(testPlan.run_test_plan(i))
        self._set_data(reportList, statistics)

        # region tool

    # 構建報告
    async def build_report(self):
        self.endTime = tool.get_cst_time()

        reportTotalData = {}
        planTestTableHtmls = []
        for item in self.reportList:
            if item.type == ReportType.TOTAL:
                for key, value in item.data.items():
                    reportTotalData.setdefault(key, [])
                    reportTotalData[key].extend(value)
            if item.type == ReportType.PLAN:
                planTestTableHtmls.append(item.data['reportHtml'])

        self.reportTotalData = reportTotalData
        htmlReport = HtmlReport()
        totalReportHtml = htmlReport.report_total_to_html(reportTotalData, True)
        elapsedTimeHtml = htmlReport.elapsed_time_to_html(self.startTime, self.endTime)
        chartHtml = htmlReport.report_line_chart_content_to_html(self.statistics)

        # reportHtml 的組成
        # baseReportHtml 一些 CSS
        # elapsedTimeHtml 經歷時間
        # totalReportHtml 總計
        # planTestTableHtml 一些測試用例
        reportHtml = self.baseReportHtml \
                     + chartHtml \
                     + self.versionHtml \
                     + elapsedTimeHtml \
                     + totalReportHtml + (htmlReport.br * 2) \
                     + (htmlReport.br * 2).join(planTestTableHtmls)

        # 寫報告實體檔案 html
        with open(self.reportPath, 'w') as f:
            f.write(reportHtml)
            f.flush()

    # 組出各別 plan 名稱
    def _find_test_dirs(self, root_dir):
        testDirs = []
        root_dir = os.path.join(self.basePath, root_dir)
        for dirPath, dirNames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.startswith('test') and filename.endswith('.json'):
                    test_dir = os.path.basename(dirPath)
                    if test_dir not in testDirs:
                        testDirs.append(test_dir)
        return sorted(testDirs)

    # 發送通知
    async def _send_notification(self):
        """
        結束後發slack通知
        """
        elapsed_time = self.endTime - self.startTime

        total_seconds = int(elapsed_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        elapsed_time = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
        reportData = self.reportTotalData
        total = sum(reportData['total'])
        passed = sum(reportData['passed'])
        failed = sum(reportData['failed'])
        slack_help.send(f'本次測試案例結果為 `total: {total}, passed: {passed}, failed: {failed}`'
                        f'\n 歷時時間: {elapsed_time} '
                        f'\n 開始時間: {self.startTime.strftime("%Y-%m-%d %H:%M:%S")}'
                        f'\n 結束時間: {self.endTime.strftime("%Y-%m-%d %H:%M:%S")}'
                        f'\n <{config.reportUrl}/{self.startTime.strftime("%Y%m%d")}/{self.reportFileName}|傳送門>')

    # 讀取 json 檔案，並回傳解析後的結果
    @staticmethod
    def _get_json(path) -> json:
        """
        讀取 json 檔案，並回傳解析後的結果
            :return: 解析後的結果
        """
        # 檢查檔案是否存在，若不存在則拋出錯誤
        if not os.path.exists(path):
            raise FileNotFoundError(f'{path} 檔案不存在')
        # 讀取任務檔案
        with open(path, 'r') as jsonString:
            return json.load(jsonString)

    # 將統計資料寫進 data-HHmm.json
    async def _save_statistics(self):
        # 寫報告實體檔案 html
        with open(self.statisticsJsonPath, 'w') as f:
            f.write(json.dumps(self.statistics[self.statisticsKey]))
            f.flush()

    # 取得n天內的統計資料
    async def _get_statistics(self):
        # 設定目錄和文件名前綴
        dir_path = os.path.join(self.basePath, 'log')
        filename_prefix = 'data'
        extension = '.json'

        # 獲取目錄下所有的子目錄並排序，最新的在前
        dirs = sorted([d for d in glob.glob(os.path.join(dir_path, '*')) if os.path.isdir(d)], reverse=True)

        # 取得最新的七個目錄
        last_7_dirs = dirs[:7]

        # 遍歷這七個目錄
        for day_dir in last_7_dirs:
            # 遍歷該目錄下的所有文件
            for filename in os.listdir(day_dir):
                # 如果文件名以指定的前綴開頭並以.json結尾
                if filename.startswith(filename_prefix) and filename.endswith(extension):
                    dayStr, timeStr = day_dir.split('/')[-1][4:], filename.split('-')[-1][:4]
                    key = f"{dayStr[:2]}-{dayStr[2:]} {timeStr[:2]}:{timeStr[2:]}"

                    with open(os.path.join(day_dir, filename), 'r') as f:
                        self.statistics[key] = json.load(f)

    def _set_data(self, reportList: list[ReportEntity], statistics: dict):
        """
        使用給定的“reportList”更新“reportList”，並使用給定的“statistics”更新“statistics”。
        Updates the `reportList` with the given `reportList` and updates the `statistics` with the given `statistics`.

        Parameters:
            reportList (dict): A dictionary representing the report list.
            statistics: The statistics to update.

        Returns:
            None
        """
        self.reportList += reportList
        for key, value in statistics.items():
            self.statistics.setdefault(key, {})
            for key2, value2 in value.items():
                self.statistics[key].setdefault(key2, 0)
                self.statistics[key][key2] += value2

    # endregion tool
