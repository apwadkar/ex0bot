import redis
import discord
import random
from discord.ext import commands
from typing import List, Optional

Members = List[discord.Member]

class Voice(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
  
  @commands.Cog.listener()
  async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel and after.channel != before.channel:
      voice_channel: discord.VoiceChannel = before.channel
      if self.cache.get(f'channel:{voice_channel.id}'):
        if not voice_channel.members:
          self.cache.delete(f'channel:{voice_channel.id}')
          await voice_channel.delete(reason='No more users left in channel')
  
  @commands.command('vcnew')
  async def vcnew(self, context: commands.Context, name: str = 'Temporary Channel', role: Optional[discord.Role] = None, limit: Optional[int] = None):
    await context.message.delete()
    voice_state: discord.VoiceState = context.author.voice
    if voice_state:
      author: discord.Member = context.author
      if role in author.roles or not role:
        parent_category: discord.CategoryChannel = voice_state.channel.category
        overwrites = {
          context.guild.default_role: discord.PermissionOverwrite(view_channel=False),
          role: discord.PermissionOverwrite(view_channel=True)
        } if role else {}
        if limit:
          voice_channel: discord.VoiceChannel = \
            await parent_category.create_voice_channel(name, overwrites=overwrites, reason=f'Temporary channel requested by {context.author}', user_limit=limit)
        else:  
          voice_channel: discord.VoiceChannel = \
            await parent_category.create_voice_channel(name, overwrites=overwrites, reason=f'Temporary channel requested by {context.author}')
        self.cache.set(f'channel:{voice_channel.id}', 1)
        await context.send('Temporary channel created. Moving you into it...')
        await author.move_to(voice_channel, reason='Moving to newly created temporary channel')
      else:
        await context.send('You do not have that role.')
    else:
      await context.send('You must be in a voice channel to make a channel.')

  @commands.command('vcmove')
  @commands.has_guild_permissions(administrator=True)
  async def vcmove(self, context: commands.Context, fromvc: discord.VoiceChannel, tovc: discord.VoiceChannel):
    await context.message.delete()
    for member in fromvc.members:
      await member.move_to(tovc, reason=f'Mass move called by {context.author}')
    await context.send(f'Successfully moved all members in {fromvc.name} to {tovc.name}')
  
  @commands.command('vcrr')
  @commands.has_guild_permissions(administrator=True)
  async def vcroulette(self, context: commands.Context, vc: Optional[discord.VoiceChannel]):
    await context.message.delete()
    if not vc:
      if context.author.voice:
        vc = context.author.voice.channel
      else:
        await context.send('You must be in a voice channel or specify a channel')
        return
    member: discord.Member = random.choice(vc.members)
    await context.send(f'{member.name} has been eliminated from {vc.name} by {context.author.mention}')
    await member.move_to(None, reason=f'Eliminated')