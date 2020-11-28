from decouple import config

CHROMEDRIVER_PATH = config('CHROMEDRIVER_PATH')
GOOGLE_CHROME_BIN = config('GOOGLE_CHROME_BIN')
USE_BIN = config('USE_BIN', cast=bool)
DEBUG = config('DEBUG', cast=bool)
API_URL = config('API_URL')
REDISTOGO_URL = config('REDISTOGO_URL')
