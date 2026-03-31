import enum

from utils import tool


class ReportType(enum.Enum):
    ELAPSED_TIME = 1  # 歷時時間
    VERSION = 2  # 版號
    TOTAL = 3  # 總數
    PLAN = 4  # 測試組


class ReportEntity:
    def __init__(self, type: ReportType, data: dict):
        self.type = type
        self.data = data


class Report:

    @staticmethod
    def setPlanTest(case, status_code, elapsedRequestTimeReportStr):
        """
        Args:
            case: case
            status_code: int
            elapsedRequestTimeReportStr: str
        """
        traceId = 'response.headers is None'
        if case.response and hasattr(case.response, 'headers'):
            traceId = case.response.headers.get('trace_id', '')
        errorStr = '\n'.join([
            f'[{case.http.method}] [{case.serverName}] {case.http.url}',
            f'traceId：{traceId}',
            f',\n'.join(case.message),
            case.responseBody
        ])

        endTime = tool.get_cst_time()
        delta = endTime - case.startTime
        case.reportData = {
            '進度': f'{case.rows}/{case.count}',
            '狀態': 'PASSED' if case.isPass else 'FAILED',
            '測試用例': f'{case.planName}-{case.name}',
            'status_code': status_code,
            '請求執行時間': elapsedRequestTimeReportStr + 's',
            '實際時間': f'{round(delta.total_seconds(), 3)}s',
            '開始時間': case.startTime.strftime("%H:%M:%S.%f")[:-3],
            '結束時間': endTime.strftime("%H:%M:%S.%f")[:-3],
            'url<br>預期結果有誤': '' if case.isPass else errorStr
        }

    @staticmethod
    def getElapsedTime(startTime, endTime):
        """
        Args:
            startTime: 開始時間
            endTime: 結束時間
        """
        elapsed_time = endTime - startTime

        total_seconds = int(elapsed_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        data = {
            '歷時時間': ['{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)],
            '開始時間': [startTime.strftime("%Y-%m-%d %H:%M:%S")],
            '結束時間': [endTime.strftime("%Y-%m-%d %H:%M:%S")]
        }
        return data
