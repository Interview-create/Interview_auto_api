import ssl

from utils import config
from slack_webhook import slack_webhook

webhook_url = config.slack.url
channel = config.slack.channel
username = config.slack.username


def send(message: str):
    if not config.notificationCenter.get('slack', {}).get('switch', False):
        return

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context_dict = ssl_context.__dict__

    slack = slack_webhook.Slack(url=webhook_url)
    # 將消息中的超連結替換為 Slack 格式的超連結
    message = message.replace("<a href=", "<").replace("</a>", ">")
    slack.post(text=message, channel=channel, username=username, icon_emoji=':robot_face:', ssl=ssl_context_dict)
