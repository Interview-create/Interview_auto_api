from entity.request_entity import TestCase
from utils import oracle_help, config


def main(case: TestCase, isRequest: bool, **kwargs):
    """
    執行 oracle sql script
    """
    try:

        if isRequest:

            setting = case.setting
            executeOracleSql = setting.get('execute_oracle_sql', None)
            if not executeOracleSql:
                raise "execute_oracle_sql 不能為空"

            # 準備連線 oracle
            # 建立連接
            connectionSettings = setting.get('connection_settings', {})
            oracle = connectionSettings.get('oracle', config.connectionSettings[case.serverName]['oracle'])
            if oracle is None:
                return

            connection = oracle_help.connect(
                username=oracle.get('username', ''),
                password=oracle.get('password', ''),
                host=oracle.get('host', ''),
                port=oracle.get('port', ''),
                sid=oracle.get('sid', '')
            )

            for filename in executeOracleSql:
                with open(filename, 'r') as f:
                    # 執行 SQL 語句
                    sql = f.read()
                    row_count = oracle_help.execute_and_return_rows(connection, sql)
                    print(f"{filename} 成功執行，總共有 {row_count} 個資料")

            return

    except Exception as e:
        case.message.append('execute_oracle_sql event 錯誤：' + str(e))
