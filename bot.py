import redis
import discord

# Settings
import settings

# Connect to Redis backend cache
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class DiscordClient(discord.Client):
    async def on_ready(self):
        # Confirm that we logged into the bot user successfully
        print(f'Logged on as {self}!')
    
    async def on_message(self, message):
        # Ignore any messages from self
        if message.author != self.user:
            print('Message from {0.author}: {0.content}'.format(message))

# Connect to Discord bot user
disc = DiscordClient()
disc.run(settings.DISCORD_TOKEN)