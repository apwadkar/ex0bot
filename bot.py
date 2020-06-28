import redis
import discord
from discord.ext import commands
from cogs.kick import Kick
from cogs.role import Role
from cogs.announce import Announce
from cogs.counter import Counter
from cogs.voice import Voice
from typing import List

# Settings
import settings

# Connect to Redis backend cache
cache = redis.Redis.from_url(url=settings.REDIS_URL)

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
  # Confirm that we logged into the bot user successfully
  print(f'Logged on as {bot.user}!')

@bot.command(name="stop")
async def stop(context: commands.Context):
  await context.message.delete()
  if context.author.guild_permissions.administrator:
    await context.send('Shutting off Ex0bot...')
    await bot.close()
  else:
    await context.send(f'{context.author()} is unable to stop the bot!')

@bot.event
async def on_message(message: discord.Message):
  # Ignore any messages from self
  if message.author != bot.user:
    # print('Message from {0.author}: {0.content}'.format(message))
    await bot.process_commands(message)

bot.add_cog(Kick(cache))
bot.add_cog(Role(bot, cache))
bot.add_cog(Announce(bot, cache))
bot.add_cog(Counter(cache))
bot.add_cog(Voice(cache))

bot.run(settings.DISCORD_TOKEN)
