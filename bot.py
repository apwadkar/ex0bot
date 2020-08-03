import redis
import discord
import datetime
from discord.ext import commands
from cogs.kick import Kick
from cogs.role import Role
from cogs.announce import Announce
from cogs.counter import Counter
from cogs.voice import Voice
from utils.logs import Logger
from typing import List

# Settings
import settings

# Connect to Redis backend cache
cache = redis.Redis.from_url(url=settings.REDIS_URL)

bot = commands.Bot(command_prefix='$')

async def patch_show():
  today = datetime.date.today()
  date_string = today.strftime('%m-%d-%Y')
  file_name = f'patch-notes/{date_string}.txt'
  with open(file_name, 'r') as patch_notes:
    notes = patch_notes.read()
    for guild in bot.guilds:
      channel = cache.hget(f'guild:{guild.id}', 'patchchannel')
      guild: discord.Guild = guild
      if channel:
        await guild.get_channel(int(channel)).send(embed=discord.Embed(
          title=f'Patch notes for {date_string}',
          description=notes
        ))

@bot.event
async def on_ready():
  # Confirm that we logged into the bot user successfully
  await patch_show()
  print(f'Logged on as {bot.user}!')

@bot.command(name="stop")
@commands.has_guild_permissions(administrator=True)
async def stop(context: commands.Context):
  await context.message.delete()
  await context.send('Shutting off Ex0bot...')
  await bot.close()
  cache.close()

@bot.command(name="patchlink")
@commands.has_guild_permissions(administrator=True)
async def patchlink(context: commands.Context, channel: discord.TextChannel):
  await context.message.delete()
  cache.hset(f'guild:{context.guild.id}', 'patchchannel', channel.id)
  await context.send(f'Linked channel {channel.mention} for patch notes')

@bot.event
async def on_message(message: discord.Message):
  # Ignore any messages from self
  if message.author != bot.user:
    await bot.process_commands(message)

logger = Logger(cache)

bot.add_cog(logger)
bot.add_cog(Kick(cache, logger))
bot.add_cog(Role(bot, cache))
bot.add_cog(Announce(bot, cache, logger))
bot.add_cog(Counter(cache))
bot.add_cog(Voice(cache))

bot.run(settings.DISCORD_TOKEN)
