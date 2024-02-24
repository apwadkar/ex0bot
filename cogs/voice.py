import redis
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

class Voice(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
  
  @commands.Cog.listener()
  async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    before_channel: discord.VoiceChannel = before.channel
    after_channel: discord.VoiceChannel = after.channel
    if before_channel and after_channel != before_channel and self.cache.get(f'tempchannel:{before_channel.id}'):
      if not before_channel.members:
        self.cache.delete(f'tempchannel:{before_channel.id}')
        await before_channel.delete(reason='No more users left in channel')
    if after_channel and self.cache.get(f'channel:{after_channel.id}'):
      parent_category: discord.CategoryChannel = after_channel.category
      overwrites = {
        member: discord.PermissionOverwrite(manage_channels=True, manage_permissions=True)
      }
      voice_channel: discord.VoiceChannel = \
        await parent_category.create_voice_channel('Temp VC', overwrites=overwrites, reason=f'Temporary channel requested by {member}')
      await member.move_to(voice_channel)
      self.cache.set(f'tempchannel:{voice_channel.id}', 1)
  
  @commands.hybrid_group(name='vc')
  async def vc(self, context: commands.Context):
    """
    Voice channel related commands
    """
    await context.message.delete()
  
  # This should create and link the staging VC for creating a new temp vc
  @vc.command('link')
  @app_commands.default_permissions(administrator=True)
  @app_commands.guild_only()
  @commands.has_guild_permissions(administrator = True)
  async def vctemplink(self, context: commands.Context, channel: discord.VoiceChannel):
    """
    Link the staging voice channel for temporary voice channels

    Parameters
    ----------
    channel: `discord.VoiceChannel`
      Staging channel to link
    """
    self.cache.set(f'channel:{channel.id}', 1)
    await context.send(f'{channel.name} has been linked', ephemeral=True)
  
  @vc.command('unlink')
  @app_commands.default_permissions(administrator=True)
  @app_commands.guild_only()
  @commands.has_guild_permissions(administrator = True)
  async def vctempunlink(self, context: commands.Context, channel: discord.VoiceChannel):
    """
    Unlink the staging voice channel for temporary voice channels

    Parameters
    ----------
    channel: `discord.VoiceChannel`
      Staging channel to unlink
    """
    self.cache.delete(f'channel:{channel.id}')
    await context.send(f'{channel.name} has been unlinked', ephemeral=True)

  @vc.command('new')
  @app_commands.guild_only()
  async def vcnew(self, context: commands.Context, name: str = 'Temporary Channel', role: Optional[discord.Role] = None, limit: Optional[int] = None):
    """
    Create a new temporary voice channel and move you in it

    Parameters
    ----------
    name: `str`
      Name of the voice channel
    role: Optional[`discord.Role`]
      Role to limit access to
    limit: Optional[`int`]
      Limit of users in the voice channel
    """
    author: discord.Member = context.author
    voice_state: discord.VoiceState = context.author.voice
    if voice_state:
      if not role or role in author.roles:
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
        self.cache.set(f'tempchannel:{voice_channel.id}', 1)
        await context.send('Temporary channel created. Moving you into it...', ephemeral=True)
        await author.move_to(voice_channel, reason='Moving to newly created temporary channel')
      else:
        await context.send('You do not have that role.', ephemeral=True)
    else:
      await context.send('You must be in a voice channel to make a channel.', ephemeral=True)