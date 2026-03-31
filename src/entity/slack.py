# 定義 Slack 類別
class Slack:
    """
    初始化 Http 類別。
    參數:
        url (str): slack url。
        channel (str): slack channel。
        username (str): slack username。
    """
    def __init__(self, data: dict):
        self.url = data.get('webhook_url', '')
        self.channel = data.get('channel', '')
        self.username = data.get('username', '')
