import redis
import discord
from discord.ext import commands
from functools import reduce
from typing import List

def announce_key(message_id):
  return f'announce:{message_id}'

class Announce(commands.Cog):
  def __init__(self, bot: discord.Client, cache: redis.Redis):
    self.cache = cache
    self.bot = bot
    self.subcommands = dict({
      'create': self.create,
      'remove': self.remove,
      'delete': self.remove,
      'remind': self.remind,
      'edit': self.edit,
      'unlink': self.unlink,
      'suggest': self.suggest
    })
  
  async def announce_create(self, author: discord.Member, title: str, description: str, announce_channel: discord.TextChannel, *reactions):
    embed = discord.Embed(
      title=title,
      description=description
    ).set_author(name=author.name, icon_url=author.avatar_url)
    message: discord.Message = await announce_channel.send(embed=embed)
    embed.set_footer(text=f'{message.id}')
    await message.edit(embed=embed)
    for reaction in reactions:
      await message.add_reaction(reaction)
      role: discord.Role = await announce_channel.guild.create_role(name=f'{title}:{reaction}', mentionable=True)
      self.cache.hset(announce_key(message.id), key=f'{reaction}', value=role.id)

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    channel: discord.Channel = self.bot.get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)
    user: discord.Member = channel.guild.get_member(payload.user_id)
    guild: discord.Guild = user.guild
    if user != message.guild.me:
      suggested = bool(self.cache.hget(name=announce_key(message.id), key='suggested'))
      if suggested:
        if payload.emoji == '👍':
          announce_id = self.cache.hget(f'announcement:{guild.id}', key='channelid')
          if not announce_id:
            await message.channel.send('You must link an announcement channel!')
          else:
            size = int(self.cache.llen(f'{announce_key(message.id)}:reacts'))
            reactions = [x.decode('utf-8') for x in self.cache.lrange(f'{announce_key(message.id)}:reacts', 0, size)]
            title = self.cache.hget(announce_key(message.id), key='title').decode('utf-8')
            description = self.cache.hget(announce_key(message.id), key='description').decode('utf-8')
            author = guild.get_member(int(self.cache.hget(announce_key(message.id), key='requester')))
            await self.announce_create(author, title, description, guild.get_channel(int(announce_id)), *reactions)
            self.cache.delete(announce_key(message.id), f'{announce_key(message.id)}:reacts')
            await message.delete()
        elif payload.emoji == '👎':
          # TODO: Request a reason and send reason to original author
          self.cache.delete(announce_key(message.id), f'{announce_key(message.id)}:reacts')
          await message.delete()
      else:
        roleid = self.cache.hget(name=announce_key(message.id), key=f'{payload.emoji}')
        if roleid:
          role = guild.get_role(int(roleid))
          await user.add_roles(role)
  
  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
    channel: discord.Channel = self.bot.get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)
    user: discord.Member = channel.guild.get_member(payload.user_id)
    if user != message.guild.me:
      roleid = self.cache.hget(name=announce_key(message.id), key=f'{payload.emoji}')
      if roleid:
        role = user.guild.get_role(int(roleid))
        await user.remove_roles(role)
  
  @commands.Cog.listener()
  async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
    message: discord.Message = reaction.message
    guild: discord.Guild = message.guild
    if user != guild.me:
      suggested = bool(self.cache.hget(name=announce_key(message.id), key='suggested'))
      if suggested:
        if reaction.emoji == '👍':
          announce_id = self.cache.hget(f'announcement:{guild.id}', key='channelid')
          if not announce_id:
            await message.channel.send('You must link an announcement channel!')
          else:
            size = int(self.cache.llen(f'{announce_key(message.id)}:reacts'))
            reactions = [x.decode('utf-8') for x in self.cache.lrange(f'{announce_key(message.id)}:reacts', 0, size)]
            title = self.cache.hget(announce_key(message.id), key='title').decode('utf-8')
            description = self.cache.hget(announce_key(message.id), key='description').decode('utf-8')
            author = guild.get_member(int(self.cache.hget(announce_key(message.id), key='requester')))
            await self.announce_create(author, title, description, guild.get_channel(int(announce_id)), *reactions)
            self.cache.delete(announce_key(message.id), f'{announce_key(message.id)}:reacts')
            await message.delete()
        elif reaction.emoji == '👎':
          # TODO: Request a reason and send reason to original author
          author: discord.Member = guild.get_member(int(self.cache.hget(announce_key(message.id), key='requester')))
          await author.send('Your announcement has been rejected by an admin')
          await message.delete()
      else:
        roleid = self.cache.hget(name=announce_key(message.id), key=f'{reaction}')
        if roleid:
          role: discord.Role = user.guild.get_role(int(roleid))
          await user.add_roles(role)

  @commands.Cog.listener()
  async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
    if user != reaction.message.guild.me:
      message: discord.Message = reaction.message
      roleid = self.cache.hget(name=announce_key(message.id), key=f'{reaction}')
      if roleid:
        role: discord.Role  = user.guild.get_role(int(roleid))
        await user.remove_roles(role)
  
  @commands.command(name='announce')
  @commands.has_role('Announcer')
  async def announce(self, context: commands.Context, subcommand: str, *args):
    subcommandFunc = self.subcommands.get(subcommand, '')
    if subcommandFunc == '':
      await context.message.delete()
      await context.send('Invalid announce subcommand!')
    else:
      await context.invoke(subcommandFunc, *args)

  @commands.command(name='announcec')
  @commands.has_role('Announcer')
  async def create(self, context: commands.Context, title: str, description: str, *reactions):
    await context.message.delete()
    author: discord.Member = context.author
    await self.announce_create(author, title, description, context.channel, *reactions)

  @commands.command(name='announcee')
  @commands.has_role('Announcer')
  async def edit(self, context: commands.Context, messageid: str, description: str):
    await context.message.delete()
    message: discord.Message = await context.channel.fetch_message(int(messageid))
    embed: discord.Embed = message.embeds[0]
    embed.description = description
    await message.edit(embed=embed)

  @commands.command(name='announced')
  @commands.has_role('Announcer')
  async def remove(self, context: commands.Context, messageid: str):
    await context.message.delete()
    message: discord.Message = await context.channel.fetch_message(int(messageid))
    suggested = bool(self.cache.hget(announce_key(messageid), key='suggested'))
    if not suggested:
      for reaction in message.reactions:
        roleid = self.cache.hget(announce_key(messageid), key=f'{reaction}')
        await context.guild.get_role(int(roleid)).delete()
    else:
      self.cache.delete(f'{announce_key(messageid)}:reacts')
    await message.delete()
    self.cache.delete(announce_key(messageid))

  @commands.command(name='announcer')
  @commands.has_role('Announcer')
  async def remind(self, context: commands.Context, messageid: str, reaction: str, reminder: str):
    await context.message.delete()
    # Check if message is actually an announcement message
    roleid = self.cache.hget(announce_key(messageid), key=f'{reaction}')
    if roleid:
      role: discord.Role = context.guild.get_role(int(roleid))
      await context.send(f'{role.mention}: {reminder}')
  
  @commands.command(name='announcel')
  @commands.has_guild_permissions(administrator=True)
  async def link(self, context: commands.Context, announcement: discord.TextChannel, admin: discord.TextChannel):
    await context.message.delete()
    self.cache.hset(f'announcement:{context.guild.id}', key='channelid', value=announcement.id)
    self.cache.hset(f'announcement:{context.guild.id}', key='adminchannelid', value=admin.id)
    await context.send(f'{announcement.mention} and {admin.mention} linked for announcement suggestions')
  
  @commands.command(name='announceul')
  @commands.has_guild_permissions(administrator=True)
  async def unlink(self, context: commands.Context, confirm: bool = False):
    await context.message.delete()
    if not confirm:
      await context.send('Confirm whether you really want to unlink the channels: $announceul yes or $announce unlink yes')
    else:
      self.cache.hdel(f'announcement:{context.guild.id}', 'channelid', 'adminchannelid')
      await context.send('Channels unlinked!')

  @commands.command(name='announces')
  async def suggest(self, context: commands.Context, title: str, description: str, *reactions):
    # Send a message in the *linked* admin chat with an embed of the message
    # Admin reacts :+1: or :-1: to accept or reject announcement
    # If accepted, send in *linked* announcement chat
    # Else, DM author saying announcement was rejected
    await context.message.delete()
    adminid = self.cache.hget(f'announcement:{context.guild.id}', key='adminchannelid')
    if not adminid:
      await context.send('You have not linked an admin channel for suggestions.')
    else:
      admin: discord.TextChannel = context.guild.get_channel(int(adminid))
      author: discord.Member = context.author
      approval_embed = discord.Embed(
        title='Approve this announcement',
        description=f'{author.name} is requesting admin approval for this announcement.'
      ).set_author(name=author.name, icon_url=author.avatar_url)
      approval_embed.add_field(name='Title', value=title, inline=False)
      approval_embed.add_field(name='Description', value=description, inline=False)
      # TODO: Don't require reactions
      approval_embed.add_field(name='Reactions', value=reduce(lambda current_string, react: f'{current_string} {react}', reactions, ''), inline=False)
      message: discord.Message = await admin.send(embed=approval_embed)
      approval_embed.set_footer(text=f'{message.id}')
      await message.edit(embed=approval_embed)
      await message.add_reaction('👍')
      await message.add_reaction('👎')
      self.cache.hmset(announce_key(message.id), {
        'suggested': 1,
        'requester': author.id,
        'title': title,
        'description': description
      })
      self.cache.lpush(f'{announce_key(message.id)}:reacts', *reactions)
      await context.send(f'Your announcement has been sent to admins for approval.')
