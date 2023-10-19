import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()


# Load environment variables with default values if not present
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY')
WTF_CSRF_ENABLED = False

CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_results',
    'CACHE_REDIS_URL': CACHE_REDIS_URL,
}

DATA_CACHE_CONFIG = CACHE_CONFIG

