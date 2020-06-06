import redis
import discord
from discord.ext import commands

class Kick(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache

  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member):
    # Restore all roles from Redis backend if an entry exists
    # await add_roles(*[role_ids])
    memberId = member.id
    rolename = f'roles:{member.guild.id}:{memberId}'
    username = f'user:{member.guild.id}:{memberId}'
    length = self.cache.llen(rolename)
    roles = self.cache.lrange(rolename, 0, length)
    roles = [member.guild.get_role(int(r)) for r in roles]
    nick = self.cache.get(username).decode('utf-8')
    self.cache.delete(rolename, username)
    await member.edit(nick=nick, roles=roles, reason='Restoring properties after server removal')

  @commands.Cog.listener()
  async def on_member_remove(self, member: discord.Member):
    # TODO: Consider just making this a command in case of user leaving (command)
    # Save all roles and nickname into the Redis backend
    # Format: roles:{user_id} as list containing all role ids, user:{user_id} as nickname
    memberId = member.id
    roleIds = [role.id for role in member.roles]
    self.cache.rpush(f'roles:{member.guild.id}:{memberId}', *roleIds)
    self.cache.set(f'user:{member.guild.id}:{memberId}', member.nick or '')

  @commands.command(name='kick')
  @commands.has_guild_permissions(kick_members=True)
  async def kick(self, context: commands.Context, user: discord.Member, reason: str = 'Kicked by admin'):
    await context.message.delete()
    await user.kick(reason=reason)
    await context.send(f'Kicked {user} for "{reason}".')