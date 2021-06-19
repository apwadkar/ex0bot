import redis
import discord
from discord.ext import commands

def log_key(guild_id):
  return f'guild:{guild_id}'

class Logger(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
  
  @commands.command(name='loglink')
  @commands.has_guild_permissions(administrator=True)
  async def loglink(self, context: commands.Context, channel: discord.TextChannel):
    await context.message.delete()
    self.cache.hset(log_key(context.guild.id), 'logchannel', channel.id)
    await context.send(f'Linked channel {channel.mention} for logging')
  
  def get_channel(self, guild: discord.Guild) -> discord.TextChannel:
    channel_id = self.cache.hget(log_key(guild.id), 'logchannel')
    if channel_id:
      return guild.get_channel(int(channel_id))
  
  async def log(self, module: type, message: str, guild: discord.Guild):
    channel = self.get_channel(guild)
    await channel.send(f'{module.__name__}: {message}')