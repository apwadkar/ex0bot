import redis
import discord
import random
from discord.ext import commands
from typing import Optional
from utils.logs import Logger

def karma_key(guild_id: int) -> str:
  return f'karma:{guild_id}'

class Karma(commands.Cog):
  def __init__(self, bot: discord.Client, cache: redis.Redis, logger: Logger):
    self.bot = bot
    self.cache = cache
    self.logger = logger

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)
    author_id: int = message.author.id
    key = karma_key(message.guild.id)
    if self.cache.sismember(f'{key}:channels', channel.id) and payload.member.id != author_id:
      if self.cache.sismember(f'{key}:positive', str(payload.emoji)):
        self.cache.hincrby(key, author_id, 1)
      elif self.cache.sismember(f'{key}:negative', str(payload.emoji)):
        self.cache.hincrby(key, author_id, -1)
  
  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
    channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)
    author_id: int = message.author.id
    key = karma_key(message.guild.id)
    if self.cache.sismember(f'{key}:channels', channel.id) and payload.member.id != author_id:
      if self.cache.sismember(f'{key}:positive', str(payload.emoji)):
        self.cache.hincrby(key, author_id, -1)
      elif self.cache.sismember(f'{key}:negative', str(payload.emoji)):
        self.cache.hincrby(key, author_id, 1)

  @commands.group(name='karma')
  async def karma(self, context: commands.Context):
    await context.message.delete()
    if not context.invoked_subcommand:
      await context.send('Invalid subcommand')
  
  @karma.command(name='get')
  async def get(self, context: commands.Context, user: Optional[discord.Member]):
    key = karma_key(context.guild.id)
    user_karma = 0
    if user:
      self.cache.hsetnx(key, user.id, 0)
      user_karma = int(self.cache.hget(key, user.id))
      await context.send(f'{user.mention} has {user_karma} karma')
    else:
      self.cache.hsetnx(key, context.author.id, 0)
      user_karma = int(self.cache.hget(key, context.author.id))
      await context.send(f'{context.author.mention} has {user_karma} karma')
  
  @karma.command(name='link')
  @commands.has_guild_permissions(administrator=True)
  async def link(self, context: commands.Context, channel: discord.TextChannel):
    self.cache.sadd(f'{karma_key(context.guild.id)}:channels', channel.id)
    await context.send(f'Linked {channel.mention} for karma tracking')
  
  @karma.command(name='unlink')
  @commands.has_guild_permissions(administrator=True)
  async def unlink(self, context: commands.Context, channel: discord.TextChannel):
    self.cache.srem(f'{karma_key(context.guild.id)}:channels', channel.id)
    await context.send(f'Unlinked {channel.mention} for karma tracking')
  
  @karma.command(name='emojis')
  @commands.has_guild_permissions(administrator=True)
  async def emojis(self, context: commands.Context, positive: discord.PartialEmoji, negative: Optional[discord.PartialEmoji]):
    key = karma_key(context.guild.id)
    self.cache.sadd(f'{key}:positive', str(positive))
    await context.send(f'{positive} has been set as a positive karma emoji')
    if negative:
      self.cache.sadd(f'{key}:negative', str(negative))
      await context.send(f'{negative} has been set as a negative karma emoji')