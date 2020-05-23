import redis
import discord
from discord.ext import commands

class Role(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
  
  @commands.Cog.listener()
  async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
    if user != reaction.message.guild.me:
      message: discord.Message = reaction.message
      roleid = self.cache.hget(name=f'role:{message.id}', key='roleid')
      if roleid:
        role = user.guild.get_role(int(roleid))
        await user.add_roles(role)

  @commands.Cog.listener()
  async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
    if user != reaction.message.guild.me:
      message = reaction.message
      roleid = self.cache.hget(name=f'role:{message.id}', key='roleid')
      if roleid:
        role = user.guild.get_role(int(roleid))
        await user.remove_roles(role)

  @commands.group(name='role')
  async def role(self, context: commands.Context, subcommand: str, *args):
    await context.message.delete()
    if subcommand == 'create':
      if len(args) == 1:
        await self.create(context, args[0])
      else:
        await self.create(context, args[0], args[1])
    elif subcommand == 'remove':
      await self.remove(context, args[0])
    else:
      await context.send('Invalid role subcommand!')
  
  async def create(self, context: commands.Context, name: str, channelName: str = ''):
    guild: discord.Guild = context.guild
    try:
      role: discord.Role = await guild.create_role(name=name, reason=f'Requested by {context.author}')
      if channelName:
        embed = discord.Embed(
          title=f'Opt in to the {name} role',
          description=f'If you\'d like access to the {name} role and {channelName} channel, react 👍.'
        )
        msg: discord.Message = await context.channel.send(embed=embed)
        self.cache.hset(name=f'role:{msg.id}', key='roleid', value=role.id)
        await msg.add_reaction('👍')
        overwrites = {
          guild.default_role: discord.PermissionOverwrite(read_messages=False),
          guild.me: discord.PermissionOverwrite(read_messages=True),
          role: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await guild.create_text_channel(name=channelName, overwrites=overwrites)
        self.cache.hset(name=f'role:{msg.id}', key='channelid', value=channel.id)
      else:
        embed = discord.Embed(
          title=f'Opt in to the {name} role',
          description=f'If you\'d like access to the {name} role, react 👍.',
        )
        msg: discord.Message = await context.channel.send(embed=embed)
        self.cache.hset(name=f'role:{msg.id}', key='roleid', value=role.id)
        await msg.add_reaction('👍')
    except discord.Forbidden as ex:
      context.send(f'{context.author} does not have sufficient privileges!')
  
  async def remove(self, context: commands.Context, messageid: str):
    roleid = self.cache.hget(f'role:{messageid}', 'roleid')
    if roleid:
      channel: discord.TextChannel = context.channel
      message: discord.Message = await channel.fetch_message(int(messageid))
      await message.delete()
      role: discord.Role = channel.guild.get_role(int(roleid))
      await role.delete(reason=f'Delete requested by {context.author}')
      channelid = self.cache.hget(f'role:{messageid}', 'channelid')
      if channelid:
        channel: discord.TextChannel = channel.guild.get_channel(int(channelid))
        await channel.delete(reason=f'Delete requested by {context.author}')
      self.cache.delete(f'role:{messageid}')