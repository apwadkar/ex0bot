import redis
import discord
from discord.ext import commands
from typing import List

class Announce(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
  
  @commands.Cog.listener()
  async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
    if user != reaction.message.guild.me:
      message: discord.Message = reaction.message
      roleid = self.cache.hget(name=f'announce:{message.id}', key=f'{reaction}')
      if roleid:
        role: discord.Role = user.guild.get_role(int(roleid))
        await user.add_roles(role)

  @commands.Cog.listener()
  async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
    if user != reaction.message.guild.me:
      message: discord.Message = reaction.message
      roleid = self.cache.hget(name=f'announce:{message.id}', key=f'{reaction}')
      if roleid:
        role: discord.Role  = user.guild.get_role(int(roleid))
        await user.remove_roles(role)
  
  @commands.command(name='announce')
  @commands.has_role('Announcer')
  async def announce(self, context: commands.Context, subcommand: str, *args):
    if subcommand == 'create':
      await context.invoke(self.create, *args)
    if subcommand == 'remove' or subcommand == 'delete':
      await context.invoke(self.remove, *args)
    if subcommand == 'remind':
      await context.invoke(self.remind, *args)
    else:
      await context.message.delete()
      await context.send('Invalid announce subcommand!')

  @commands.command(name='announcec')
  @commands.has_role('Announcer')
  async def create(self, context: commands.Context, title: str, description: str, *reactions):
    await context.message.delete()
    author: discord.Member = context.author
    embed = discord.Embed(
      title=title,
      description=description
    ).set_author(name=author.name, icon_url=author.avatar_url)
    message: discord.Message = await context.send(embed=embed)
    for reaction in reactions:
      await message.add_reaction(reaction)
      role: discord.Role = await context.guild.create_role(name=f'{title}:{reaction}', mentionable=True)
      self.cache.hset(f'announce:{message.id}', key=f'{reaction}', value=role.id)

  @commands.command(name='announced')
  @commands.has_role('Announcer')
  async def remove(self, context: commands.Context, messageid: str):
    await context.message.delete()
    message: discord.Message = await context.channel.fetch_message(int(messageid))
    for reaction in message.reactions:
      roleid = self.cache.hget(f'announce:{messageid}', key=f'{reaction}')
      role: discord.Role = context.guild.get_role(int(roleid))
      await role.delete()
    await message.delete()
    self.cache.delete(f'announce:{messageid}')

  @commands.command(name='announcer')
  @commands.has_role('Announcer')
  async def remind(self, context: commands.Context, messageid: str, reaction: str, reminder: str):
    await context.message.delete()
    # Check if message is actually an announcement message
    roleid = self.cache.hget(f'announce:{messageid}', key=f'{reaction}')
    if roleid:
      role: discord.Role = context.guild.get_role(int(roleid))
      await context.send(f'{role.mention}: {reminder}')