from flask import Flask
from redis import Redis

import settings

cache = Redis.from_url(url=settings.REDIS_URL)

app = Flask(__name__)

@app.route('/')
def home_view():
  return '<h1>test</h1>'

if __name__ == '__main__':
  app.run()