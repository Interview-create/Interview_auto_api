import redis


class RedisHelper:
    def __init__(self, host='localhost', port=6379, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.pool = redis.ConnectionPool(
            host=self.host, port=self.port, password=self.password)

    def get_conn(self):
        return redis.Redis(connection_pool=self.pool)

    def set_value(self, key, value):
        r = self.get_conn()
        r.set(key, value)

    def get_value(self, key):
        r = self.get_conn()
        return r.get(key)

    def delete(self, key):
        r = self.get_conn()
        for key in r.keys(key):
            r.delete(key)
