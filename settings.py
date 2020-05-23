from dotenv import load_dotenv
import os

load_dotenv()

# Redis connection info
REDIS_URL = os.getenv('REDIS_URL') or ''

# Discord info
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or ''
OWNER_ID = os.getenv('OWNER_ID') or ''