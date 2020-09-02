import redis
import discord
from discord.ext import commands

class Poll(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
  
  @commands.command(name='pollemo')
  @commands.has_guild_permissions(administrator=True)
  async def pollemo(self, context: commands.Context):
    await context.message.delete()
    # self.cache.hset(f'poll:{context.guild}', 'upvote', upvote.id)
    # self.cache.hset(f'poll:{context.guild}', 'downvote', downvote.id)
    await context.send('This feature is not implemented yet!')

  @commands.command(name='pollc')
  async def pollc(self, context: commands.Context, title: str, desc: str):
    await context.message.delete()
    embed = discord.Embed(
      title = title,
      description = desc
    )
    message: discord.Message = await context.send(embed=embed)
    embed.set_footer(text=message.id)
    await message.edit(embed=embed)
    await message.add_reaction('👍')
    await message.add_reaction('👎')
  
  @commands.command(name='polld')
  @commands.has_guild_permissions(manage_messages=True)
  async def polld(self, context: commands.Context, message: discord.Message):
    await context.message.delete()
    await message.delete()