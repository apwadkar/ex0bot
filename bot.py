import redis
import discord
from discord.ext import commands
from cogs.kick import Kick
from cogs.role import Role
from cogs.announce import Announce
from cogs.counter import Counter
from typing import List

# Settings
import settings

# Connect to Redis backend cache
cache = redis.Redis.from_url(url=settings.REDIS_URL)

bot = commands.Bot(command_prefix='$')

# async def restore_cache(bot: discord.Client, cache: redis.Redis, pattern: str):
#   keys: List(str) = cache.keys(pattern)
#   for key in keys:
#     msgid = key[len(pattern) - 1:]
#     for guild in bot.guilds:
#       for channel in guild.channels:
#         if type(channel) is discord.TextChannel:
#           try:
#             await channel.fetch_message(int(msgid))
#             print(f'Restoring {msgid}')
#             break
#           except discord.NotFound:
#             print(f'Not in channel {channel}')
#   print(f'Restored messages for {pattern}')

@bot.event
async def on_ready():
  # Confirm that we logged into the bot user successfully
  print(f'Logged on as {bot.user}!')
  # TODO: Cache role and announce messages from redis
  # await restore_cache(bot, cache, 'roles:*')
  # await restore_cache(bot, cache, 'announce:*')
  # for msg in bot.cached_messages:
  #   print(f'Cached message: {msg.id}')

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

bot.run(settings.DISCORD_TOKEN)
