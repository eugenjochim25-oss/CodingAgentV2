import redis
from config import Config

config = Config()

redis_client = redis.Redis(host='localhost', port=6379, db=0)
