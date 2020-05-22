from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST=os.getenv('REDIS_HOST') or 'localhost'
REDIS_PORT=int(os.getenv('REDIS_PORT') or '6379')
REDIS_DB=int(os.getenv('REDIS_DB') or '0')