import logging
import os
import time

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# 定義日誌文件路徑
LOG_PATH = os.path.join(BASE_PATH, "log", f'{time.strftime("%Y%m%d")}')
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)


class Logger:

    def __init__(self, name):
        if not bool(name):
            name = 'default'
        else:
            name = f'{name}-{time.strftime("%H%M%S")}'

        # 設定日誌檔名
        self.logname = os.path.join(LOG_PATH, f'{name}.log')
        # 建立日誌物件，並以日誌檔名作為日誌物件的名稱
        self.logger = logging.getLogger(self.logname)
        # 設定日誌記錄等級
        self.logger.setLevel(logging.DEBUG)
        # 建立日誌格式
        self.formatter = logging.Formatter('[%(asctime)s][%(filename)s %(lineno)d][%(levelname)s]: %(message)s')
        # 建立日誌檔案監聽器
        self.filelogger = logging.FileHandler(self.logname, mode='a', encoding="UTF-8")
        self.filelogger.setLevel(logging.DEBUG)
        self.filelogger.setFormatter(self.formatter)
        self.logger.addHandler(self.filelogger)

        self.console = logging.StreamHandler()
        self.console.setLevel(logging.ERROR)
        self.console.setFormatter(self.formatter)
        self.logger.addHandler(self.console)

        # 刪除 logger 中之前的 handler，只保留現在添加的
        self.logger.handlers = []
        self.logger.addHandler(self.filelogger)
        self.logger.addHandler(self.console)


logger = Logger('').logger

if __name__ == '__main__':
    logger.info("---測試開始---")
    logger.debug("---測試結束---")
