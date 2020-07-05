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
  async def vcmove(self, context: commands.Context, fromvc: discord.VoiceChannel, tovc: discord.VoiceChannel):
    await context.message.delete()
    for member in fromvc.members:
      await member.move_to(tovc, reason=f"Mass move called by {context.author}")
    await context.send(f"Successfully moved all members in {fromvc.name} to {tovc.name}")