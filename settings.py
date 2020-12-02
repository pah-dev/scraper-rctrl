import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN')
USE_BIN = bool(os.environ.get('USE_BIN', False))
DEBUG = bool(os.environ.get('DEBUG', False))
HOST_URL = os.environ.get('HOST_URL')
API_URL = os.environ.get('API_URL')
REDISTOGO_URL = os.environ.get('REDISTOGO_URL')
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = os.environ.get('SECRET_KEY')
