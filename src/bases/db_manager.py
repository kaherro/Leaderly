import redis

class DBManager:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self._connect()
        
    def _connect(self):
        try:
            self.r = redis.Redis(host=self.host, port=self.port, decode_responses=True)
            self.r.ping()
            print("Connected to Redis successfully!")
        except redis.exceptions.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
            self.r = None
