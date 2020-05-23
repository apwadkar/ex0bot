import redis
import discord
from discord.ext import commands

class Kick(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache

  @commands.Cog.listener()
  async def on_member_add(self, member: discord.Member):
    # Restore all roles from Redis backend if an entry exists
    # await add_roles(*[role_ids])
    name = f'role:{member.id}'
    length = self.cache.llen(name)
    roles = self.cache.lrange(name, 0, length)
    nick = self.cache.get(f'user:{member.id}')
    await member.edit(nick=nick, roles=roles, reason="Restoring properties after server removal")

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
  async def kick(self, context: commands.Context, user: discord.Member, reason: str = 'Kicked by admin'):
    await context.message.delete()
    invoker: discord.Member = context.message.author
    try:
      await user.kick(reason=reason)
      await context.send(f'Kicked {user} kicked for "{reason}".')
    except discord.Forbidden:
      await context.send(f'Unable to kick {user} because {invoker} does not have permissions.')