import redis
import discord
from discord.ext import commands

class Role(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache

  @commands.command(name='role')
  async def role(self, context: commands.Context, name: str, channelName: str = ''):
    # TODO: Figure out how bool converters work
    await context.message.delete()
    guild: discord.Guild = context.guild
    guild.create_role(name=name, reason=f'Requested by {context.author}')
    if channelName:
      await context.send(f'Creating role {name} with channel {channelName}')
    else:
      await context.send(f'Creating role {name} with no channel')