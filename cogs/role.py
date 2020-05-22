import discord
from discord.ext import commands

class Role(commands.Cog):
  @commands.command(name='role')
  async def role(self, context: commands.Context, name: str, channelName: str, createChannel: bool = True):
    # Figure out how bool converters work
    pass