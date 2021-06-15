import redis
import discord
import random
from discord.ext import commands
from typing import List, Optional
from utils.logs import Logger

class Karma(commands.Cog):
  def __init__(self, bot: discord.Client, cache: redis.Redis, logger: Logger):
    self.bot = bot
    self.cache = cache
    self.logger = logger

  async def react_add(self, guild: discord.Guild, channel: discord.TextChannel, emoji_id: int, message: discord.Message):
    if self.cache.sismember(f'karma:{guild.id}', channel.id):
      if self.cache.sismember(f'kemoji:positive:{guild.id}', emoji_id):
        self.logger.log(type(self), 'positive emoji', guild)
        print('positive emoji ')
      elif self.cache.sismember(f'kemoji:negative:{guild.id}', emoji_id):
        self.logger.log(type(self), 'positive emoji', guild)
        print('negative emoji ')
  
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    guild: discord.Guild = self.bot.get_guild(payload.guild_id)
    message: discord.Message = await guild.fetch_message(payload.message_id)
    channel: discord.TextChannel = guild.get_channel(payload.channel_id)
    await self.react_add(guild, channel, payload.emoji.id, message)

  @commands.group(name='karma')
  async def karma(self, context: commands.Context):
    if not context.invoked_subcommand:
      await context.message.delete()
      await context.send('Invalid subcommand')
  
  @karma.command(name='link')
  @commands.has_guild_permissions(administrator=True)
  async def link(self, context: commands.Context, channel: discord.TextChannel):
    self.cache.sadd(f'karma:{context.guild.id}', channel.id)
    await context.send(f'Linked {channel.mention} for karma tracking')
  
  @karma.command(name='unlink')
  @commands.has_guild_permissions(administrator=True)
  async def unlink(self, context: commands.Context, channel: discord.TextChannel):
    self.cache.srem(f'karma:{context.guild.id}', channel.id)
    await context.send(f'Unlinked {channel.mention} for karma tracking')
  
  @karma.command(name='emojis')
  @commands.has_guild_permissions(administrator=True)
  async def emojis(self, context: commands.Context, positive: discord.Emoji, negative: discord.Emoji):
    # TODO: Add support for "awards"
    self.cache.sadd(f'kemoji:positive:{context.guild.id}', positive.id)
    self.cache.sadd(f'kemoji:negative:{context.guild.id}', negative.id)