import redis
import discord
import random
from discord.ext import commands
from typing import Optional, List
from utils.logs import Logger
from itertools import islice
import datetime

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
    if self.cache.sismember(f'{key}:channels', channel.id) and payload.user_id != author_id:
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
    if self.cache.sismember(f'{key}:channels', channel.id) and payload.user_id != author_id:
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
  
  @karma.command(name='resetall')
  @commands.has_guild_permissions(administrator=True)
  async def resetall(self, context: commands.Context):
    self.cache.delete(karma_key(context.guild.id))
    await context.send(f'{context.guild} has been reset for karma tracking')
  
  @karma.command(name='init')
  @commands.has_guild_permissions(administrator=True)
  async def init_server(self, context: commands.Context):
    for user in context.guild.members:
      self.cache.hsetnx(karma_key(context.guild.id), user.id, 0)
    await context.send(f'Set all users in {context.guild} to 0 if they did not have karma before')

  @karma.command(name='set')
  @commands.has_guild_permissions(administrator=True)
  async def set(self, context: commands.Context, user: discord.Member, value: int):
    self.cache.hset(karma_key(context.guild.id), user.id, value)
    await context.send(f'{user.mention} has been set to {value} karma')

  @karma.command(name='leaderboard')
  async def leaderboard(self, context: commands.Context, tops: int = 10):
    # TODO: List top 10 people and bottom 10 people
    keys = [int(key) for key in self.cache.hkeys(karma_key(context.guild.id))]
    vals = dict((key, int(self.cache.hget(karma_key(context.guild.id), key))) for key in keys)
    val_map = lambda id: f'{context.guild.get_member(id)}: {vals[id]}'
    sorted_vals = map(val_map, islice(sorted(vals, key=vals.get, reverse=True), tops))
    rev_sorted_vals = map(val_map, islice(sorted(vals, key=vals.get), tops))
    embed = discord.Embed(
      title=f'Karma Leaderboard for {context.guild}',
      color=discord.Color.random(),
      timestamp=datetime.datetime.now()
    ) \
      .set_author(name=context.author.name, icon_url=context.author.avatar_url) \
      .set_thumbnail(url=context.guild.icon_url) \
      .add_field(name='Top 10', value='\n'.join(sorted_vals)) \
      .add_field(name='Bottom 10', value='\n'.join(rev_sorted_vals))
    await context.send(embed=embed)
    
  
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