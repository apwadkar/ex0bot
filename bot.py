import redis
import discord
from datetime import datetime
from pytz import timezone
from discord.ext import commands
from cogs.karma import Karma
from cogs.kick import Kick
from cogs.role import Role
from cogs.announce import Announce
from cogs.counter import Counter
from cogs.voice import Voice
from cogs.poll import Poll
from cogs.bestof import Bestof
from utils.logs import Logger
from typing import List

# Settings
import settings

# Connect to Redis backend cache
cache = redis.Redis.from_url(url=settings.REDIS_URL)

logger = Logger(cache)

# Configure member caching intent
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

async def patch_show():
  aztz = timezone('America/Phoenix')
  today = datetime.now(aztz)
  date_string = today.strftime('%m-%d-%Y')
  file_name = f'patch-notes/{date_string}.txt'
  try:
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
  except:
    pass

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
  # Ignore any messages from self or blocked people
  if message.author != bot.user and not cache.sismember('blocked', message.author.id):
    await bot.process_commands(message)

bot.add_cog(logger)
bot.add_cog(Kick(cache, logger))
bot.add_cog(Role(bot, cache))
bot.add_cog(Announce(bot, cache, logger))
bot.add_cog(Counter(cache))
bot.add_cog(Voice(cache))
bot.add_cog(Poll(cache))
bot.add_cog(Bestof(bot, cache, logger))
bot.add_cog(Karma(bot, cache, logger))

@bot.command(name='block')
@commands.has_guild_permissions(administrator=True)
async def block(context: commands.Context, member: discord.Member):
  await context.message.delete()
  cache.sadd('blocked', member.id)
  await context.send(f'Blocked {member.mention} from using bot commands')
  await logger.log(commands.Bot.__name__, f'{context.member.mention}: Blocked {member.mention} from using bot commands', context.guild)

@bot.command(name='unblock')
@commands.has_guild_permissions(administrator=True)
async def unblock(context: commands.Context, member: discord.Member):
  await context.message.delete()
  cache.srem('blocked', member.id)
  await context.send(f'Unblocked {member.mention} from using bot commands')
  await logger.log(commands.Bot.__name__, f'{context.member.mention}: Unblocked {member.mention} from using bot commands', context.guild)

bot.run(settings.DISCORD_TOKEN)
