import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('.env'))


class Config(object):
    CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
    GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN')
    USE_BIN = bool(os.environ.get('USE_BIN', False))
    DEBUG = bool(os.environ.get('DEBUG', False))
    HOST_URL = os.environ.get('HOST_URL')
    API_URL = os.environ.get('API_URL')
    PORT = int(os.environ.get('PORT', 5000))
    SECRET_KEY = os.environ.get('SECRET_KEY')
    REDISTOGO_URL = os.environ.get('REDISTOGO_URL')
    REDIS_QUEUES = os.environ.get("REDIS_QUEUES")
    REDIS_TTL = int(os.environ.get("REDIS_TTL", 10800))
    RQ_DASHBOARD_REDIS_URL = os.environ.get('REDISTOGO_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    SENTRY_URL = os.environ.get('SENTRY_URL')
    SENTRY_RATE = float(os.environ.get('SENTRY_RATE'))
