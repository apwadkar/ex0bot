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
@commands.has_guild_permissions(administrator=True)
async def stop(context: commands.Context):
  await context.message.delete()
  await context.send('Shutting off Ex0bot...')
  await bot.close()
  cache.close()

@bot.command(name="loglink")
@commands.has_guild_permissions(administrator=True)
async def loglink(context: commands.Context, channel: discord.TextChannel):
  await context.message.delete()
  cache.hset(f'guild:{context.guild.id}', 'logchannel', channel.id)
  await context.send(f'Linked channel {channel} for logging')

@bot.event
async def on_message(message: discord.Message):
  # Ignore any messages from self
  if message.author != bot.user:
    # print('Message from {0.author}: {0.content}'.format(message))
    if 'kachoe' in message.content:
      await message.channel.send('<:kachoe:737926572631392296>')
      await message.add_reaction('<:kachoe:737926572631392296>')
    await bot.process_commands(message)

bot.add_cog(Kick(cache))
bot.add_cog(Role(bot, cache))
bot.add_cog(Announce(bot, cache))
bot.add_cog(Counter(cache))
bot.add_cog(Voice(cache))

bot.run(settings.DISCORD_TOKEN)
