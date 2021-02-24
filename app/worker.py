from flask import current_app
from rq import Worker, Connection


conn = current_app.redis

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(current_app.config["REDIS_QUEUES"])
        worker.work()