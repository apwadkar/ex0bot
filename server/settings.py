from dotenv import load_dotenv
import os

load_dotenv()

# Redis connection info
REDIS_URL = os.getenv('REDIS_URL') or ''