import redis
import discord
from discord.ext import commands

class Announce(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
  
  @commands.command(name='announce')
  @commands.has_role('Announcer')
  async def announce(self, context: commands.Context, subcommand: str, *args):
    await context.message.delete()
    if subcommand == 'create':
      await context.invoke(self.create, *args)
    if subcommand == 'remove':
      await context.invoke(self.remove, *args)
    if subcommand == 'remind':
      await context.invoke(self.remind, *args)
    else:
      await context.send('Invalid announce subcommand!')

  @commands.command(name='announcec')
  @commands.has_role('Announcer')
  async def create(self, context: commands.Context, title: str, description: str, *reactions):
    pass

  @commands.command(name='announced')
  @commands.has_role('Announcer')
  async def remove(self, context: commands.Context, messageid: str):
    pass

  @commands.command(name='announcer')
  @commands.has_role('Announcer')
  async def remind(self, context: commands.Context, messageid: str, reaction: str, reminder: str):
    pass