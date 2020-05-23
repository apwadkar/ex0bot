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

  @commands.command(name='role')
  @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
  async def role(self, context: commands.Context, subcommand: str, *args):
    if subcommand == 'create':
      await context.invoke(self.create, *args)
    elif subcommand == 'remove' or subcommand == 'delete':
      await context.invoke(self.remove, *args)
    else:
      await context.message.delete()
      await context.send('Invalid role subcommand!')
  
  @commands.command(name='rolec')
  @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
  async def create(self, context: commands.Context, name: str, channelName: str = ''):
    await context.message.delete()
    guild: discord.Guild = context.guild
    # Check if the role already exists on this server
    msgrole: discord.Role = None
    for role in guild.roles:
      if role.name == name:
        msgrole = role
        break
    if not msgrole:
      msgrole = await guild.create_role(name=name, reason=f'Requested by {context.author}')

    # If a channel creation is requested, create/link one
    embed = discord.Embed(title=f'Opt in to the {name} role')
    if channelName:
      embed.description = f'If you\'d like access to the {name} role and {channelName} channel, react 👍.'
      msg: discord.Message = await context.channel.send(embed=embed)
      self.cache.hset(name=f'role:{msg.id}', key='roleid', value=msgrole.id)
      await msg.add_reaction('👍')

      # Check is channel already exists on this server
      msgchannel: discord.TextChannel = None
      for channel in guild.channels:
        if channel.name == channelName:
          msgchannel = channel
          break
      if not msgchannel:
        overwrites = {
          guild.default_role: discord.PermissionOverwrite(read_messages=False),
          guild.me: discord.PermissionOverwrite(read_messages=True),
          role: discord.PermissionOverwrite(read_messages=True)
        }
        category: discord.CategoryChannel = guild.get_channel(context.channel.category_id)
        msgchannel = await guild.create_text_channel(name=channelName, overwrites=overwrites, category=category)
      self.cache.hset(name=f'role:{msg.id}', key='channelid', value=msgchannel.id)
    else:
      embed.description=f'If you\'d like access to the {name} role, react 👍.'
      msg: discord.Message = await context.channel.send(embed=embed)
      self.cache.hset(name=f'role:{msg.id}', key='roleid', value=msgrole.id)
      await msg.add_reaction('👍')
  
  @commands.command(name='roled')
  @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
  async def remove(
    self,
    context: commands.Context,
    messageid: str,
    deleterole: bool = True,
    deletechannel: bool = True
  ):
    await context.message.delete()
    # Check if the message id was actually a role message
    roleid = self.cache.hget(f'role:{messageid}', 'roleid')
    if roleid:
      # Delete message
      channel: discord.TextChannel = context.channel
      message: discord.Message = await channel.fetch_message(int(messageid))
      await message.delete()

      # Delete role
      if deleterole:
        role: discord.Role = channel.guild.get_role(int(roleid))
        await role.delete(reason=f'Delete requested by {context.author}')

      # Check if the role has an associated channel
      channelid = self.cache.hget(f'role:{messageid}', 'channelid')
      if channelid:
        # Delete channel
        if deletechannel:
          channel: discord.TextChannel = channel.guild.get_channel(int(channelid))
          await channel.delete(reason=f'Delete requested by {context.author}')
      
      # Delete cache entry
      self.cache.delete(f'role:{messageid}')