from decouple import config

CHROMEDRIVER_PATH = config('CHROMEDRIVER_PATH')
GOOGLE_CHROME_BIN = config('GOOGLE_CHROME_BIN')
USE_BIN = config('USE_BIN', cast=bool)
DEBUG = config('DEBUG', cast=bool)
HOST_URL = config('HOST_URL')
API_URL = config('API_URL')
REDISTOGO_URL = config('REDISTOGO_URL')
PORT = config('PORT')
SECRET_KEY = config('SECRET_KEY')
