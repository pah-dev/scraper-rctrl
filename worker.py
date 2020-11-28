import redis
from rq import Worker, Queue, Connection
from settings import REDISTOGO_URL

listen = ['default']

redis_url = REDISTOGO_URL

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
