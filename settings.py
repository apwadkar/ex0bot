from dotenv import load_dotenv
import os

load_dotenv()

# Redis connection info
REDIS_HOST=os.getenv('REDIS_HOST') or 'localhost'
REDIS_PORT=int(os.getenv('REDIS_PORT') or '6379')
REDIS_DB=int(os.getenv('REDIS_DB') or '0')

# Discord info
DISCORD_TOKEN=os.getenv('DISCORD_TOKEN') or ''
OWNER_ID=os.getenv('OWNER_ID') or ''