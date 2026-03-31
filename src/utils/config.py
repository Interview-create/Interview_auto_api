import json
import os

from entity.slack import Slack

# 讀取配置檔
BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# 優先使用環境變數中的 envConfig
env_config = os.environ.get('envConfig')
if env_config is not None:
    config = json.loads(env_config)
# 如果環境變數中不存在 envConfig，則優先使用 env.json 檔案中的設定
elif os.path.isfile(f'{BASE_PATH}/env.json'):
    with open(f'{BASE_PATH}/env.json') as f:
        config = json.load(f)
# 如果 env.json 檔案不存在，則使用 config.json 檔案中的設定
elif os.path.isfile(f'{BASE_PATH}/config.json'):
    with open(f'{BASE_PATH}/config.json') as f:
        config = json.load(f)
# 如果 config.json 檔案也不存在，則拋出一個異常
else:
    raise ValueError('無法讀取配置檔案')

# 取得配置資訊
environment = config['environment']
requestVerify = config.get('request_verify', False)
env = config['env']
connectionSettings = env[environment]
defaultRequestEvents = config['default_request_events']
defaultResponseEvents = config['default_response_events']
notificationCenter = config['notification_center']
slack = Slack(notificationCenter.get('slack', {}))
versionPath = config['version_path']
queuePath = config['queue_path']
reportUrl = config['report_url']
planName = config.get('plan_name', [])
fullLog = config.get('full_log', True)
requestTimeOut = config.get('request_timeout', 60)
