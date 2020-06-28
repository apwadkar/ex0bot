import redis
import discord
from discord.ext import commands
from typing import List

Members = List[discord.Member]

class Voice(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
  
  @commands.command("vcmove")
  @commands.has_guild_permissions(administrator=True)
  def vcmove(self, context: commands.Context, fromvc: discord.VoiceChannel, tovc: discord.VoiceChannel):
    members: Members = fromvc.members
    for member in members:
      await member.move_to(tovc, reason=f"Mass move called by {context.author}")
    await context.send(f"Successfully moved all members in {fromvc.name} to {tovc.name}")