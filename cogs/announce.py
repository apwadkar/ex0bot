import discord
from discord.ext import commands

class Announce(commands.Cog):
  @commands.command(name='announce')
  async def announce(self, context: commands.Context, title: str, description: str, *reactions):
    pass