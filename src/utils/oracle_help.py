import cx_Oracle


def connect(username, password, host, port, sid):
    """建立與 Oracle 資料庫的連接"""
    dsn = cx_Oracle.makedsn(host=host, port=port, sid=sid)
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)


def disconnect(connection):
    """關閉 Oracle 資料庫的連接"""
    connection.close()


def execute(connection, sql, params=None):
    """執行 SQL 語句"""
    cursor = connection.cursor()
    cursor.execute(sql, params or [])
    return cursor


def fetchall(cursor):
    """獲取所有查詢結果"""
    return cursor.fetchall()


def fetchone(cursor):
    """獲取一條查詢結果"""
    return cursor.fetchone()


def commit(connection):
    """提交事務"""
    connection.commit()


def rollback(connection):
    """回滾事務"""
    connection.rollback()


def execute_and_return_rows(connection, sql, params=None):
    """執行 SQL 語句，返回執行結果和影響行數"""
    cursor = connection.cursor()
    cursor.execute(sql, params or [])
    # 提交事務
    row_count = cursor.rowcount
    connection.commit()
    cursor.close()
    return row_count
